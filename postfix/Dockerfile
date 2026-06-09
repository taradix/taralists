FROM alpine:3.24

RUN apk add --no-cache postfix && newaliases

COPY main.cf /etc/postfix/

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
