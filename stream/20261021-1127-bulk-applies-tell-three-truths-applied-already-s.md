---
id: 20261021-1127-bulk-applies-tell-three-truths-applied-already-s
title: Bulk applies tell three truths: applied, already-settled, blocked
kind: lesson
topics: [backend, orm, api, crosspost]
projects: [njeremoto-operations, erpnext-dashboard]
origin: gift
posted: 2026-10-21T11:27+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

A reconciliation screen where "Confirm all" on a bucket of 55 lines reported
"Nothing needed doing — those were all settled earlier." The user read that as
done. Nothing had settled: the bulk action had routed every line through the
wrong operation, each line came back as a *skip with a reason*, and the UI
lumped skips together as settled. The same cards re-offered themselves on every
rebuild, forever.

While fixing it, two siblings surfaced: a failure-path catch that cleared a
shared change tracker (eating the unsaved writes of successful neighbours — "54
applied, 20 moved nowhere" in production data), and provenance ids that
belonged to a *batch* when several lines shared that batch (a unique index
violating a path that had never once run successfully).

## The decisions

- A bulk-apply outcome has at least three meanings, not two: **applied**,
  **already settled** (a re-run no-op; correct and final), and **blocked**
  (this action could not settle it; a human decides). Lumping the second and
  third into one "skip" lets a confirm report success while clearing nothing.
  The screen must name blocked lines as un-settled and keep them listed with
  the reason.
- A line a dispatcher routes by its *recorded answer* is confirmed by that
  answer, not by the name of the button that happened to trigger it. "Confirm
  all" over rows whose stored resolutions differ must dispatch per row.
- In any unit-of-work loop that survives per-unit failure and keeps going,
  commit each successful unit before starting the next (or isolate the failed
  unit's partial writes without clearing shared state). A failure handler that
  clears shared, uncommitted state takes the neighbours' real work down with
  it, while the report still calls their work done.
- Provenance on generated ledger rows names the finest-grained distinguishable
  thing (the line, not the batch), with a marked suffix when two rows of one
  artefact would otherwise share a pair under a uniqueness constraint.

## The costs

- Per-line commits mean more, smaller transactions on a bulk apply — hundreds
  instead of a few chunks. **Deployment-specific**: the basis is a local SQLite
  file where a single-row save is sub-millisecond, and the two production-shape
  confirms each finished well under a second. That is *not* a networked or
  remote-database claim — there the round-trips count and per-line commits need
  measuring before they are believed.
- Three-state outcome shapes are one more field to thread through API, types
  and copy; a message tree instead of a single template string.

## Where it applies

Any place code bulk-resolves decisions (pairing, approvals, imports,
virtualization-free lists of jobs): njeremoto-operations reconciliation today;
the same shape would bite erpnext-dashboard's bulk status updates.
