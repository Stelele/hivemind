---
id: 20261113-2252-ef-core-sqlite-executedelete-cannot-translate-pr
title: EF Core SQLite: ExecuteDelete cannot translate predicates over converted columns
kind: lesson
topics: [efcore, sqlite, pitfalls]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-13T22:52+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

`OutboxWorker` (njeremoto-operations) failed **every 30-second dispatch cycle** with "could not be translated" — the expired-upload sweep ran `db.PendingUploads.Where(u => u.ExpiresAtUtc < DateTimeOffset.UtcNow).ExecuteDeleteAsync()` on SQLite. `ExecuteDelete` cannot translate a predicate over a column with a value converter (the entity's `DateTimeOffset` goes through a UTC converter), so the exception fired before dispatch ever ran — meaning outbox retries silently lost their timer path and only worked when an event happened to wake the drain. Found only because a smoke test happened to be running while the logs scrolled.

## What we decided

On EF Core + SQLite, never put `ExecuteDelete`/`ExecuteDeleteAsync` directly against a predicate over a converted column: load the target ids client-side (`.Where(...).Select(x => x.Id).ToListAsync()`), then delete with `ExecuteDeleteAsync(e => ids.Contains(e.Id))` — the `Guid`/unconverted key translates fine. And wrap any sweep inside a hosted worker's cycle in its own try/catch so a sweep failure can never starve the cycle's real work (dispatch, processing) — a background worker whose cleanup step aborts its job is the worst of both worlds.

## Why

`ExecuteDelete` builds a SQL `DELETE ... WHERE` straight from the expression tree; the provider must translate every term against the *store* shape, and converter-wrapped columns (dates stored as strings, money as minor units) don't survive that. Selecting ids first evaluates the predicate through the normal query pipeline (converters applied correctly), then deletes by the raw key.

## The cost

Two statements instead of one (a read then a delete — a grant expiring between them survives one cycle; harmless), and a hostile id backlog could hit SQLite's bind-parameter limit on the `IN (...)` — which the sweep's own guard now contains. Also a log-message split: sweep failures log their own line, so anything grepping the old combined failure message needs updating.
