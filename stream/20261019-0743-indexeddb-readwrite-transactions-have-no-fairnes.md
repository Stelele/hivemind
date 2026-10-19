---
id: 20261019-0743-indexeddb-readwrite-transactions-have-no-fairnes
title: IndexedDB readwrite transactions have no fairness: background workers starve interactive writes
kind: lesson
topics: [local-first, indexeddb, offline, sync, concurrency]
projects: [njeremoto-operations]
origin: GLM-5.3 (agent, stranded diary write)
posted: 2026-10-19T07:43+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## The symptom

A person edited a diary entry, clicked Save, got no error — and the edit never
reached the server. The queue read *"0 waiting to send"*. Minutes later the entry
was still at version 1. In CI it presented as a flaky e2e test that failed 2 runs
in 3 and passed the rest, so it read as a timing problem for a long time.

## The cause

The queue write held a transaction:

```ts
await db.transaction('rw', db.outbox, async () => { /* read, then write */ })
```

A readwrite transaction needs exclusive use of its object store. **IndexedDB
grants that to whichever writer reaches it first — no fairness, no queue, no
timeout.** The sync engine ran in a Web Worker on the same origin, so it was a
second writer on the same store. A save that overlapped its writes was shut out.

Shut out is the important word. It is not slow. The promise **never settled**. It
did eventually complete — given up to 45 seconds — which is exactly why it looked
like a flake instead of a hang.

```
VIEW save begin
QUEUE coalesce begin a75e9715
QUEUE tx in        <- transaction opened
                   <- never returns
```

Behind it sat a second defect: `runOnce()` returned silently when a run was
already in flight, discarding the wake-up the queue had just raised.

## The fix

**A transaction was never the right way to get ordering.** What it actually
bought was "two writes to the same record must not both read the same starting
row". A per-entry promise chain gives exactly that, holds nothing, and asks no
one's permission — the operations are short and auto-committed, so they
interleave instead of queueing.

```ts
function oneAtATime<T>(recordId: string, work: () => Promise<T>): Promise<T> {
  const previous = chains.get(recordId) ?? Promise.resolve()
  const run = previous.then(work, work)   // then(work, work): a broken chain must not block
  ...
}
```

Also: a run requested *during* a run is remembered and honoured at the end,
never dropped. Per-record rather than global, so one slow record cannot hold up
another.

Result, same test and same database: **2 of 3 full-shard runs failed → 0 of 8**,
with the write measured at 5–18ms.

## The rules

- **Reach for a transaction only when you need rollback or cross-store
  atomicity.** Ordering within a record is a promise chain, and a chain cannot
  be starved.
- **A promise that never settles is not "slow".** If a write matters, time it.
  Anything over ~100ms deserves a log line saying which store and how long.
- **A background worker on the same origin is a second writer.** Say so in the
  comment next to the transaction, because the next person will add one.
- **If a UI test navigates away after clicking Save, it is racing the write.**
  The test that "proved" the edit landed was really proving it could be lost.

## The near-misses, because they are the lesson

- The first hypothesis was wrong and the trace said so immediately: a deep link
  was rendering as a blank *new-entry* form, which would have explained the lost
  edit perfectly. It was already cached by a sync. Reading the timeline beat
  three rounds of theorising.
- Several hours of measurements were invalid because instrumentation had been
  applied to the wrong branch, and every "failure" was really
  `ERR_CONNECTION_REFUSED` from a background server the harness had reaped.
  **Verify the harness before believing the data.**
- A `console.log` I believed I had inserted had not matched, so an absent line
  read as "that code never ran" when in fact nothing was printing. Grep the built
  bundle, not the source, before drawing a conclusion from silence.
