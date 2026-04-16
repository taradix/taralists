FROM maxking/mailman-web:0.5

COPY mailman-provision.py /usr/local/bin/

RUN sed -i \
        -e 's|psql -P pager=off $DATABASE_URL -c .\\l.|pg_isready -d $DATABASE_URL|' \
        -e 's|/opt/mailman-web-data/settings_local.py|/etc/mailman-web/settings_local.py|g' \
        -e 's|exec \$@|[[ -v SERVE_FROM_DOMAIN ]] \&\& /usr/local/bin/mailman-provision.py\nexec $@|' \
        /usr/local/bin/docker-entrypoint.sh
