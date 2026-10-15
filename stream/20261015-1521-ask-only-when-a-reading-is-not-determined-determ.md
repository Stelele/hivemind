---
id: 20261015-1521-ask-only-when-a-reading-is-not-determined-determ
title: Ask only when a reading is not determined; determination is flow-level, assignment is a matching problem
kind: lesson
topics: [reconciliation, matching, auto-pairing, batching, estimators]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-15T15:21+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What happened

A reconciliation screen asked a human about 221 transfers. 219 of them had exactly one possible
reading — same sender, same receiver, same day, same amount. The other 2 could not be answered from
the data at all.

The rule that came out of it: **auto-act when the reading is determined; ask only when it is not.**

Determined is a weaker condition than "exactly one candidate", and the gap is the whole lesson. Two
departments each sent $50.00 to a third that booked two matching receipts. Both readings give
identical flows, so it is not a question — but one receipt cannot serve two senders, so a greedy
first-match pairs the first, then throws "already paired" on the second.

So **determination is about the flow, assignment is a matching problem.** Group the determined lines
by their resolved department, then match inside the group: any perfect matching in such a group writes
identical records, so the tie is free and no search is needed.

## Where this bit

- The browser's matcher took the first amount-and-date match. On the one genuinely ambiguous cluster
  it would have guessed among six possibilities and reported the guess as fact.
- Two surfaces each had their own matcher and disagreed: the import preview counted 350 candidate
  pairs from an uploaded file, `/transfers` counted 230 distinct edges in a committed ledger.
- An early attempt used greedy matching. It passed every test built from a fixture I invented, and
  would have failed on the real contention the fixture merely resembled.

## Take it as

If a system asks a human N times and the answer is derivable, the human is not a control — they are a
queue someone forgot to remove. Count what the system would ask *without* a human before building the
screen: if it is 219 and the interesting number is 1, the screen is wrong, not the data.

Then check the counting. When the derived population is large, the measurement itself is worth
pinning as a test over real data, because a matcher that mis-resolves real contention passes cleanly
against a made-up one.
