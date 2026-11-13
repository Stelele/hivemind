---
id: 20261113-2251-jev-noul-screen-validates-against-ocr-backlog-0
title: Jev noul screen validates against OCR backlog: 0 false resolves, catches bad resolves both directions
kind: lesson
topics: [review, ocr, jev, typesafe]
projects: [ocr-review, erpnext-dashboard, erpnext-point-of-sale-expenses]
origin: gift
posted: 2026-11-13T22:51+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Calibrating a Jev (System One, noul) screen for the OCR verdict sweeper against real
backlog: replayed every OCR-owned review thread from the last 2 weeks of Stelele PRs —
594 threads across 109 files (136 resolved, 458 open) — through jev-1.13-free via
OpenCode's systemone endpoint, batched per file.

Result: 593/594 judged, 0 failures, 0.8 minutes wall clock, 525k input tokens, $0 on the
free tier, no rate limiting at concurrency 2. Cross-tab vs thread state: of RESOLVED
threads only 34/136 were judged clearly fixed while 54/136 were judged still present; of
OPEN threads 48 were judged clearly fixed. Two mechanical spot-checks both confirmed Jev
against the record: a resolved thread whose fix never landed (the flagged import is still
in the file at the resolved head), and an open thread whose suggested permission check is
verbatim in the head code (fix landed, thread never resolved).

## What we decided

Pending owner decision: a two-stage gate for the verdict sweeper — jev-1.13-free noul
screen first (batched per file, near-free, ~seconds); resolve only when noul < ~0.2,
escalate the 0.2–0.7 band to the glm-5.3 verdict path. In the replay this would cut the
reasoning-LLM calls to ~30% of threads while adding an independent calibrated check.

## Why

The judgment "does the described problem still exist in this file?" is exactly a Noul,
and the replay shows its errors are one-directional (wrong calls keep threads OPEN, never
wrongly resolve) with perfect specificity on the 15-case labeled set and 2/2 mechanical
spot-check wins over the resolve record on real backlog. The typed output also deletes
the JSON-parsing failure class that consumed 4 of 11 review rounds on the sweeper.

## The cost

- Thread state is not ground truth: "clearly fixed" on an open thread can mean the fix
  landed OR the finding never applied; both are resolvable, but the resolve semantics
  differ and a human/glm audit should precede any mass resolution.
- jev-1.13 (not 1.14) via OpenCode; free-tier rate limits untested beyond ~500k tokens
  in one run — the paid tier needs Console credits, not the Go subscription.
- Open-weight System One models (Laya 421M, OpenJev 0.4B) have 256–1024-token contexts —
  structurally unable to ingest whole files, so self-hosting in Actions is a dead end
  for this task; the hosted endpoint is the path.
- One more dependency surface in CI (though auth reuses the existing OpenCode key).
