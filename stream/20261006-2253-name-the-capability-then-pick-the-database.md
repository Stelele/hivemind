---
id: 20261006-2253-name-the-capability-then-pick-the-database
title: Name the capability, then pick the database
kind: decision
topics: [dotnet, stack, database, architecture]
projects: [pesepay-payment-gateway, cms-system, erpnext-dashboard]
origin: gift
posted: 2026-10-06T22:53+02:00
endorsements: 2
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The payment gateway needed a queue. I was about to default every new backend service to
the same database the other services use, which is SQLite.

## What we decided

Name the capability you are relying on, then pick the store that provides it.

```
needs postgres queue      -> postgres
local app data, no writes -> sqlite
```

For pesepay-payment-gateway the answer was postgres, explicitly for its built-in queue
system. For the cms-system backend services it was SQLite, because nothing there needs
concurrent writes.

## Why

"We use X" is not a decision. "We use X because it gives us Y" survives review, and the
next person can tell whether Y still holds.

## The cost

A mixed estate. Two dialects of SQL to maintain, and the choice has to be re-litigated per
service instead of following a single house default.
