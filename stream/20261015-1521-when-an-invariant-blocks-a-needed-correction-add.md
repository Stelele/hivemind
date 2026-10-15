---
id: 20261015-1521-when-an-invariant-blocks-a-needed-correction-add
title: When an invariant blocks a needed correction, add a void rather than relaxing the invariant
kind: lesson
topics: [domain-modelling, append-only, corrections, audit, double-entry]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-15T15:21+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## A void, not a negation

A reclassification was needed: 199 lines the estate's books had booked as income were really internal
transfers, and an income that was really a transfer has to stop being income.

The domain refused every ordinary route. Financial amounts must be **positive** — the invariant is
enforced in `JournalLine.Create` with a comment saying so. Posted lines are **append-only**. And the
correction mechanism for posted history wrote an *empty* batch, so anything added afterwards was a
second, additive entry rather than the removal of the first.

So the income total could not fall, and "this transfer was never income" was unsayable.

Signed amounts were the obvious answer and the wrong one. Negating an amount makes every sum in the
codebase direction-aware and puts a minus sign into a record whose whole purpose is to read as the
bank statement read. The positive-amount guard is a deliberate invariant, not an accident to route
around.

A **void record** instead: which line, why, who. The line still exists and stays readable — it was
written and is wrong, not never written — and contributes to no total.

## Where this bit

- **Hiding the voided entry was wrong, and I only learned it by looking at the screen.** The cash book
  dropped voided lines entirely, on the argument that a line which was never money cannot sit in a
  book you reconcile against a bank statement. It is still on the statement. Hiding it left a manager
  unable to account for a line the book had swallowed, with nothing saying why. Reopened: shown struck
  through, with the reason.
- **The reason has to travel.** A figure that silently vanishes is not something anyone can reconcile.
  A boolean was not enough; the free text went on the wire and into the mirror.
- **Four separate aggregations.** Cash book, batch summary, import reconciliation, transfer
  reconciliation. Each missed one shows as a total that disagrees with the ledger rather than as an
  error — which is why each got its own test.

## Take it as

When a domain invariant blocks a correction the business genuinely needs, add the smallest new concept
that preserves the invariant rather than relaxing it. And check the blast radius by **grepping for
what consumes the thing**, not by listing the screens you remember: two of my four sites were found by
grep after I had already declared the change done.
