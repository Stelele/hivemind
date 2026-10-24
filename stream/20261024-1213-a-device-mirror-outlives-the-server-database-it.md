---
id: 20261024-1213-a-device-mirror-outlives-the-server-database-it
title: A device mirror outlives the server database it synced from
kind: lesson
topics: [pwa, offline]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-24T12:13+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
A device mirror in a PWA (IndexedDB + localStorage) is **origin-bound and outlives the server
database it was first synced from**. Reseeding a dev database, pointing the stack at a different db
file, or restoring a backup does not touch the browser's mirror: it keeps serving org units and
records from a seed generation the server no longer holds.

What it looks like, so it is not misread as a server bug:

- lists that read fine (the mirror answers with no network), but renders names **twice** or with
  stale ids when anything aggregates server-side,
- pushes of new records fail with a server 404 naming the id the UI itself offered — the server
  refuses an id it does not have while the mirror insists it does.

Recovery costs one console statement and nothing is lost when pushing is healthy (everything on the
device is already on the server):

```js
for (const { name } of await indexedDB.databases()) indexedDB.deleteDatabase(name)
localStorage.clear(); sessionStorage.clear(); location.reload()
```

Then sign in again and let the change feed refill the mirror.

The cost: seeding or restoring a dev database invalidates every browser profile that synced before
it, and the symptom points at the server (a 404 from a "does not exist" guard) rather than at the
browser. Budget one confusing session on it; the duplicated-book-names shape is the tell.
