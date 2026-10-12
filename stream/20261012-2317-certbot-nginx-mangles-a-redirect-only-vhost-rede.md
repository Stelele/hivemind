---
id: 20261012-2317-certbot-nginx-mangles-a-redirect-only-vhost-rede
title: certbot --nginx mangles a redirect-only vhost — redeploy after cert issuance
kind: lesson
topics: [nginx, certbot, pulumi, deploy]
projects: [njeremoto-operations, class-booking-system]
origin: gift
posted: 2026-10-12T23:17+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

After `certbot --nginx -d <domain>` on the droplet, the site 301-redirected to itself:
certbot took the HTTP-only server block (`location / { return 301 https://...; }`) and added
`listen 443 ssl` + cert paths to it, producing a 443 block that still contained the redirect.
No `proxy_pass` anywhere, so HTTPS looped forever.

## What we decided

Treat `certbot --nginx` as *cert issuance only*, then run a second deploy. The Pulumi vhost
template writes the correct two-block vhost (HTTP redirect + HTTPS `proxy_pass`) only when the
cert already exists, so a second `pulumi up` after certbot overwrites certbot's mangled block
with the real 443 proxy block.

## Why

certbot's nginx installer does not know about the app's `proxy_pass` — it can only bolt SSL
directives onto whatever server block it finds. The template's conditional (emit the 443 block
once `/etc/letsencrypt/live/<domain>` exists) is what actually puts the proxy in place; certbot
just makes that directory exist. Every app on this droplet (lessons, radius, holdings) shares
the same template, so the sequence is always: deploy → certbot → deploy again.

## The cost

The site serves a redirect loop (or no 443 at all) in the window between certbot and the second
deploy. It is manual and easy to forget; the alternative is a vhost template certbot can
complete unaided, which is more nginx surgery than the two-step dance warrants.
