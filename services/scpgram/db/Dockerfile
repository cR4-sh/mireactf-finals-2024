FROM postgres:13.3


ENV TZ=Europe/Moscow

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY init.sql /docker-entrypoint-initdb.d/database.sql