FROM ubuntu:jammy-20240416

WORKDIR /opt/app
COPY acms .

RUN apt update && apt install socat postgresql-client libpq-dev -yyy && \
    adduser user && \
    chmod 555 acms

USER user
CMD ["socat", "tcp-l:10079,reuseaddr,fork", "EXEC:'/opt/app/acms',pty,echo=0,raw"]
