FROM alpine:latest
WORKDIR /init
COPY ./schemas /init
COPY wait_to_start.sh /init
RUN apk add --update curl
CMD ["sh", "wait_to_start.sh"]