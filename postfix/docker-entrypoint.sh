#!/bin/sh
set -e

postconf -e "myhostname=${SERVER_HOSTNAME:-localhost}"
postconf -e "relayhost=[${RELAYHOST:-localhost}]:${RELAYHOST_PORT:-25}"

# Reload postfix when mailman updates its lookup tables
(
    last=""
    while true; do
        sleep 10
        current=$(stat -c %Y /opt/mailman/var/data/postfix_lmtp 2>/dev/null || echo "")
        if [ -n "$current" ] && [ "$current" != "$last" ]; then
            last=$current
            postfix reload 2>/dev/null || true
        fi
    done
) &

exec postfix start-fg
