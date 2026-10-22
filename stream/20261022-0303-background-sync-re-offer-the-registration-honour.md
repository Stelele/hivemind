---
id: 20261022-0303-background-sync-re-offer-the-registration-honour
title: Background Sync: re-offer the registration, honour lastChance
kind: lesson
topics: [pwa, offline, service-worker]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-22T03:03+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Auditing the Chrome DevTools Application-tab APIs against our PWA found that Background Sync was offered
once per page load in `begin()`. One-shot registrations are spent the first time they fire, so by the time
anybody went offline during the day the offer was already consumed: writes queued offline, app closed,
connectivity returns → no pending registration → nothing drains until somebody reopens the app. That is
exactly the window the API exists to cover. Separately, the service worker ignored `event.lastChance` —
the browser's final attempt — so a row abandoned there kept a raw `503` in `lastError` and stayed
`sending` until the 60s claim timeout, and nothing in /sync could tell "backoff" from "nobody will ever
retry this".

## What we decided

In any web app with a service-worker background drain: re-offer `sync.register(tag)` on every `offline`
transition and after each queued write (the browser collapses repeat registrations for the same tag, so
the cost is a no-op call when online), and treat `lastChance === true` as a distinct regime — release +
mark the failing row, do not rethrow, keep draining the rest, and rewrite the row's error to say the
browser gave up. Keep the throw *before* lastChance: it is what schedules the browser's own retry backoff.

## Why

The registration lifetime is the whole model of Background Sync and it is invisible in the docs-level
usage: one `register()` at load looks correct and covers nothing. The offline transition is precisely the
moment the browser promises to fire a pending registration when connectivity returns, app open or not.
`lastChance` is the only signal the promise chain ends there; ignoring it makes every later row state a
small lie.

## The cost

Two extra `register()` calls per enqueue/offline cycle (collapsed server-side by the browser, a real
call each time regardless), and the give-up wording on a row must now be read in /sync as a distinct
state — a pending row whose error says "stopped retrying" until the next app open resurrects it. The
extracted drain (`lib/sync/outboxDrain.ts`) is one more file between the service worker and its trigger.
