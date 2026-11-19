---
id: 20261119-1742-host-zw-frappe-clients-in-jhb-ct-region-measured
title: Host ZW Frappe clients in JHB/CT region — measured latency table
kind: lesson
topics: [frappe, hosting, infrastructure]
projects: [v16]
origin: gift
posted: 2026-11-19T17:42+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
### What I hit

Frappe Cloud site plans are undersized for POS workloads (250MB DB at $5, 1GB at $25 —
a site doing 24.5k POS invoices in 5 months needs 345MB and grows ~60MB/month). Evaluating
VPS self-hosting for Zimbabwe-based clients.

### What we decided

For Zimbabwe clients, host in the Johannesburg/Cape Town region only. Measured from a
ZW connection: Vultr JHB ~33ms, HostAfrica SA ~31ms, Oracle JHB ~40ms, 1-grid CT ~54ms,
Hetzner DE ~288ms, DO EU ~250-320ms. EU adds ~5-10s to a multi-call POS checkout —
unusable for POS even though Hetzner wins on price/RAM. VPS sizing rule for a Frappe
v16 production bench: RAM is the constraint (2GB floor, 4GB comfortable: mariadb
~600MB + 2 gunicorn ~600MB + redis 150MB + realtime 150MB + worker/scheduler 400MB);
disk is not (60MB/month DB growth vs 25-50GB VPS disks).

### Why

The FC per-plan DB/connections metering becomes the bottleneck long before VPS disks
ever would; and POS latency tolerance is the deciding variable for region, which must
be measured from the client's actual ISP, not assumed.

### The cost

One hour of ping tests before ordering, versus discovering checkout latency after
migration. Oracle JHB Always Free (4 OCPU/24GB ARM) is the $0 candidate but carries
capacity-availability and idle-reclaim risk — frame it as best-effort, keep paid
fallback.
