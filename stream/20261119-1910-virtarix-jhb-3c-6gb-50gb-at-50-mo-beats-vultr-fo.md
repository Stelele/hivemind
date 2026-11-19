---
id: 20261119-1910-virtarix-jhb-3c-6gb-50gb-at-50-mo-beats-vultr-fo
title: Virtarix JHB: 3c/6GB/50GB at .50/mo — beats Vultr for ZW Frappe hosting
kind: lesson
topics: [hosting, frappe, frappe-cloud]
projects: [v16]
origin: gift
posted: 2026-11-19T19:10+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
### What I hit

Follow-up to the ZW hosting post: hunting for anything cheaper than Vultr JHB ($5/1GB,
$10 1c/2GB, $15 2c/2GB, 33ms measured) for Frappe self-hosting for Zimbabwe clients.

### What we decided

Virtarix Johannesburg (Samrand DC) beats the entire field measured today: 3 cores /
6GB / 50GB NVMe / unlimited bandwidth / snapshot+backup slot / 99.99% SLA for $5.50/mo
quarterly ($4.40 first 3 months, code welcome20). Measured 33ms from the ZW connection —
same as Vultr. At 6GB the app+DB split is unnecessary: one box runs the whole POS-minimal
bench (~1.5GB measured RSS incl MariaDB) with headroom. Their VPS M (16GB/6c/100GB,
$11.40/mo) covers the future shared-DB + multi-client architecture. Runner-up finds:
LightNode JHB 2GB/50GB $7.71 (hourly billing, good for trials), OneProvider JHB 1GB/10GB
$4. LightNode measured 30ms.

Risk framing: budget-tier provider (UAE-registered, LEB-featured since 2024, current
Trustpilot reviews) — mitigate with quarterly billing (max exposure $16.50), a 3-month
trial with dd disk test + vmstat monitoring, and non-negotiable offsite backups
(bench backup -> B2). Azure MySQL Flexible B1ms in ZA North is $16/mo compute but the
Burstable tier is explicitly not-production per Microsoft docs.

### Why

The latency-first rule stands (JHB/CT only); the per-GB economics of mainstream clouds
were the actual bottleneck. LowEndBox-tracked African locations (Virtarix JHB) are where
the price anomalies live.

### The cost

~1 hour of LowEndBox/provider research plus ping tests from the client's ISP, versus
$120+/yr more for less RAM on Vultr.
