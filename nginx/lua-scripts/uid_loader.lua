local _M = {}

function _M.load_uids(file_path)
    local uid_list = ngx.shared.uid_list
    local f = io.open(file_path, "r")
    if not f then
        ngx.log(ngx.ERR, "Не удалось открыть файл UID: ", file_path)
        return
    end

    for line in f:lines() do
        local uid = line:match("^%s*(%d+)%s*$")
        if uid then
            uid_list:set(uid, true)
        end
    end

    f:close()
end

return _M
