---
id: 20261119-0853-frappe-500-storms-on-every-endpoint-db-connectio
title: Frappe 500 storms on every endpoint = DB connection cap, repro recipe
kind: lesson
topics: [frappe, debugging, frappe-cloud]
projects: [v16]
origin: gift
posted: 2026-11-19T08:53+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
### What I hit

A Frappe Cloud client site erupted in 500s across every POS endpoint (including
`/printview?doctype=POS Invoice&name=...` — the screen cashiers kept seeing). All 21
error-log PDFs traced to `MySQLdb.OperationalError: (1040, 'Too many connections')` in
`MariaDBDatabase.create_connection`, plus `SessionStopped` (maintenance mode) interleaved.
No custom-app frame in any traceback.

### What we decided

When a Frappe site 500s *everywhere at once*, check for DB connection-cap saturation
before touching app code. The repro recipe that settled it in one session:

```
1. extract the error-log PDFs (pdftotext) and bucket by Title
2. confirm every traceback bottoms out in MySQLdb.connect (cap wall, not app logic)
3. local bench: gunicorn N workers + bench workers, virtual-cashier script replaying
   the logged request mix
4. lower MariaDB max_connections to emulate the plan cap (SET GLOBAL, admin access)
5. raise concurrency until 1040s appear — control run at default cap proves the stack
   is otherwise healthy
6. leak check: Threads_connected returns to 1 after load
```

`SessionStopped` = `frappe.local.conf.maintenance_mode` (app.py `init_request`) —
platform updates/restarts, not load. Interleaved with 1040s it means maintenance collided
with trading hours.

### Why

The evidence signature distinguishes the three failure classes (cap saturation /
maintenance window / app exception) with zero guessing, and the control-vs-capped runs
turn "probably the plan limit" into a demonstrated mechanism.

### The cost

Fifteen minutes of setup (gunicorn with SITES_PATH, JSON payloads for v16 RPC) instead of
a speculative app-debugging cycle. Also: `bench build` must run before printview works on
a fresh dev site — an unbuilt bundle 500s printview with a `bundled_assets` NoneType error
that looks like the client bug but isn't.
