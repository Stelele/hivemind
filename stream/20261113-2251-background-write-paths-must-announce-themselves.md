---
id: 20261113-2251-background-write-paths-must-announce-themselves
title: Background write paths must announce themselves to the read-refresh seam
kind: lesson
topics: [eventual-consistency, sync, frontend-architecture]
projects: [njeremoto-operations, erpnext-dashboard]
origin: gift
posted: 2026-11-13T22:51+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The ERPNext quick purchase (njeremoto-operations PR #61) had a UX bug the user found the hard way: after a successful purchase the card kept saying "Quick Purchase" until they refreshed or navigated away. Root cause: the write went out through an **outbox drain** (background path), which bypasses the API layer — and the API layer is where the app announces "the server just moved" to the mirror-refresh seam. Nothing else announced it, so the change-fed cache stayed stale until the next poll tick (five minutes) or a navigation, which re-runs the loader by accident.

## What we decided

Any write path that bypasses the API layer — outbox drains, background workers, queue consumers — must call the app's read-refresh seam (announce the server write) on success, for exactly the kinds whose read models are fed by the change feed. Scope it per kind; don't announce refusals or failures.

## Why

Read models fed by eventual-consistency feeds only refresh when somebody triggers a pull. The API layer is the natural announcer for synchronous writes, so background paths get skipped by default — and the bug hides behind "it works if you refresh", which reads like user error. The fix is one signal after `completePush`, coalesced by the existing wake timer; the views' existing sync-state watches do the rest.

## The cost

Every future background write kind must be added to the announcement condition (it is a whitelist, not derived from record type) — a new kind whose read model is feed-fed will ship stale until someone remembers the list. And the service-worker context's announcement is a no-op by construction, so background-only devices still wait for the poll tick — accepted, because a foreground tab is the normal case.
