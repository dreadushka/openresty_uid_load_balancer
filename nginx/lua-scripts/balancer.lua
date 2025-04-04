local balancer = {}
local resty_lock = require "resty.lock"
local lrucache = require "resty.lrucache"
local cjson = require "cjson"

-- Конфигурация
local upstreams = {
    app1 = "app1:5000",
    app2 = "app2:5000"
}

-- Глобальные объекты
local uid_cache = ngx.shared.uid_cache
local lru_cache, err = lrucache.new(1000)  -- 1000 элементов LRU-кеша
local lock = resty_lock:new("balancer_dict")

-- Загрузка UID из файла в shared memory
local function load_uids()
    local cache, err = lock:lock("uid_loader")
    if not cache then
        ngx.log(ngx.ERR, "Failed to acquire lock: ", err)
        return
    end

    local file = io.open("/etc/nginx/uids.lst", "r")
    if not file then
        ngx.log(ngx.ERR, "Failed to open uids.lst")
        lock:unlock()
        return
    end

    -- Очищаем текущий кеш
    uid_cache:flush_all()

    local count = 0
    for line in file:lines() do
        local uid = line:gsub("%s+", "")
        if #uid > 0 then
            uid_cache:set(uid, true)
            count = count + 1
        end
    end

    ngx.log(ngx.INFO, "Loaded ", count, " UIDs into shared memory")
    file:close()
    lock:unlock()
end

-- Инициализация
function balancer.init()
    -- Первичная загрузка
    load_uids()

    -- Периодическая перезагрузка каждые 30 сек
    local ok, err = ngx.timer.every(30, function()
        load_uids()
    end)
    
    if not ok then
        ngx.log(ngx.ERR, "Failed to create timer: ", err)
    end
end

-- Основная логика балансировки
function balancer.handle_request()
    -- 1. Проверяем cookie
    local cookie = ngx.var.cookie_special_user
    if cookie then
        ngx.var.backend = upstreams.app2
        ngx.exec("@proxy")
        return
    end

    -- 2. Получаем UID из параметра
    local uid = ngx.var.arg_uid

    -- 3. Если UID не указан - отправляем на app1
    if not uid then
        ngx.var.backend = upstreams.app1
        ngx.exec("@proxy")
        return
    end

    -- 4. Проверяем LRU-кеш
    local is_special = lru_cache:get(uid)
    if is_special == nil then
        -- Проверяем shared memory
        is_special = uid_cache:get(uid) or false
        
        -- Сохраняем в LRU-кеш (10 сек)
        lru_cache:set(uid, is_special, 10)
    end

    -- 5. Принимаем решение
    if is_special then
        ngx.header["Set-Cookie"] = "special_user=1; Path=/; Max-Age=3600; SameSite=Lax"
        ngx.var.backend = upstreams.app2
    else
        ngx.var.backend = upstreams.app1
    end

    ngx.exec("@proxy")
end

return balancer
