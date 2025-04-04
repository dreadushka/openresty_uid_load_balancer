FROM openresty/openresty:alpine

# Устанавливаем зависимости
RUN apk add --no-cache --update \
    gcc \
    musl-dev \
    make \
    openssl-dev \
    pcre-dev \
    wget \
    luajit-dev  # Заголовочные файлы LuaJIT

# Устанавливаем LuaRocks для LuaJIT
RUN wget https://luarocks.org/releases/luarocks-3.9.2.tar.gz && \
    tar zxpf luarocks-3.9.2.tar.gz && \
    cd luarocks-3.9.2 && \
    ./configure \
        --prefix=/usr/local/openresty/luajit \
        --with-lua=/usr/local/openresty/luajit \
        --with-lua-include=/usr/include/luajit-2.1 && \
    make && make install && \
    cd .. && rm -rf luarocks-3.9.2*

# Настройка переменных окружения
ENV PATH=$PATH:/usr/local/openresty/luajit/bin
ENV LUA_PATH="/usr/local/openresty/luajit/share/lua/5.1/?.lua;/usr/local/openresty/nginx/lua-scripts/?.lua;;"
ENV LUA_CPATH="/usr/local/openresty/luajit/lib/lua/5.1/?.so;;"

# Устанавливаем Lua-модули
RUN luarocks install lua-resty-lrucache && \
    luarocks install penlight && \
    luarocks install lua-cjson

# Чистим кэш
RUN rm -rf /var/cache/apk/* && \
    rm -rf /usr/local/openresty/luajit/lib/luarocks/cache/*

COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
COPY lua-scripts /usr/local/openresty/nginx/lua-scripts

EXPOSE 80
