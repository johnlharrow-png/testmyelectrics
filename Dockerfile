# testmyelectrics.com — static site served by Caddy on Railway
FROM caddy:2-alpine
COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html /srv/index.html
COPY robots.txt sitemap.xml /srv/
COPY assets /srv/assets
