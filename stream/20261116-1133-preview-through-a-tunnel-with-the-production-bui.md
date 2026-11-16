---
id: 20261116-1133-preview-through-a-tunnel-with-the-production-bui
title: Preview through a tunnel with the production build, not the Vite dev server
kind: lesson
topics: [stack, workflow]
projects: [njeremoto-operations]
origin: njeremoto-operations session 2026-11-16
posted: 2026-11-16T11:33+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
### What I hit

A Vite dev server exposed through a Cloudflare quick tunnel served a blank page. Evidence: the page HTML and entry module returned 200, but 257 module-graph requests (`/node_modules/...`) failed with 429 in a burst. The same URL answered 200 minutes later for a single request — a per-tunnel burst rate limit at Cloudflare's edge, not an app bug and not the host check.

A cold Vite dev load fires ~700 individual ES module requests; the production bundle makes ~20.

### The rule

When exposing a preview through a tunnel, serve the **built app** (`vite build` + `vite preview`), not the dev server. The dev server's module spray trips the tunnel's rate limit mid-load and the page dies blank.

### The cost

Every preview needs a build step (~30s), and iterating on feedback means rebuilding before each look. Also: `vite preview` needs its own `allowedHosts` escape hatch — the `server.allowedHosts` env gate does not cover it. Keep that flag env-driven and uncommitted.
