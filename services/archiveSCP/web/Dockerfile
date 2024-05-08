FROM golang:1.21.5-alpine3.18

WORKDIR /usr/src/app

COPY go.mod go.sum* ./
RUN go mod download && go mod verify
EXPOSE 8000

ENV secret=bebebe
COPY ./ ./
RUN go build -o /usr/local/bin/app

CMD ["app"]