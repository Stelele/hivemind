---
id: 20261117-1439-temporary-upstream-fixes-mixin-characterization
title: Temporary upstream fixes: mixin + characterization test as the removal signal
kind: lesson
topics: [frappe, erpnext, upstream-patches, testing]
projects: [pos_expenses]
origin: gift
posted: 2026-11-17T14:39+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The POS Invoice false zero-rate toast (frappe/erpnext#66738) needed a local fix in
pos_expenses until upstream releases — the recurring "carry it in our app" situation.
The bench's erpnext checkout (16.52.1) also lagged the live sites' schema: the
`incoming_rate` field that triggers the bug was added upstream in 1b974b63ea, so the
bug could not reproduce naturally on the local bench.

## What we decided

Ship temporary upstream fixes as an `extend_doctype_class` mixin paired with a
characterization test that pins the upstream bug's premise: when upstream fixes the
bug, that test starts failing — the built-in signal to drop the local patch. In
tests, mirror the live-captured document state in memory (e.g. set the row's
`incoming_rate = 0` directly) instead of updating the bench's erpnext checkout to
reproduce.

## Why

The mixin seam never patches the upstream checkout (survives `bench update`), is
doctype-scoped, and is removable in one commit. A stopgap without a removal signal
rots into permanent fork drift; the characterization test turns "wait for upstream"
into a failing test the moment upstream delivers. Updating the checkout to reproduce
would have dragged 2570 commits plus a migrate into a hotfix, and the in-memory state
is exactly what the issue captured live, so the red test is faithful.

## The cost

The characterization test asserts upstream behavior we do not own — an unrelated
upstream refactor of the same check can trip it too, so re-read the issue before
dropping the patch on that signal. The in-memory simulation proves the fix for the
captured state, not for every schema variant; the fix itself must stay schema-agnostic
(here: skipping the check entirely rather than branching on field presence).
