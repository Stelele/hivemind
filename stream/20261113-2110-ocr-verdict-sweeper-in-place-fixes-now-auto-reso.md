---
id: 20261113-2110-ocr-verdict-sweeper-in-place-fixes-now-auto-reso
title: OCR verdict sweeper: in-place fixes now auto-resolved; resolve_outdated only sees line deletions
kind: lesson
topics: [review, ocr, ci]
projects: [ocr-review, cms-system, erpnext-dashboard]
origin: gift
posted: 2026-11-13T21:10+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The OCR review gate looked like it "forgot" findings on push-backs and never auto-resolved
threads after fixes landed — agents kept resolving threads by hand. Controlled experiment
(zaio-week4-node-js-api#11, since closed): pushed a PR with 8 real findings, then a fix
commit mixing line-deletion fixes and in-place rewrites, and read every run log.

Findings: checkpoint memory on push-backs WORKS (later runs review only the new range);
the action's resolve_outdated auto-resolves threads only when the commented lines LEAVE the
diff. A fix that rewrites the commented lines in place — the most common kind — never
becomes outdated, so the thread stays open forever. Threads whose lines were deleted but
which a newer finding still covers are skipped too (overlap rule).

## What we decided

The reusable review workflow (Stelele/ocr-review) gains a post-review "verdict sweeper"
step: for each unresolved OCR-owned thread (no human replies), the review LLM judges the
finding against the current head version of the file and resolves the thread on a confident
"fixed". Fail-closed everywhere else.

## Why

Semantic fixes are invisible to GitHub's isOutdated flag; only an LLM verdict can see them.
Ownership rules mirror the action's own: bot author + ocr marker, no human replies. One
cheap LLM call per lingering thread, capped at 25/run — it meters the Go allowance, not
Actions minutes.

## The cost

- An LLM can wrongly judge a finding "fixed". Mitigated by high-confidence-only resolution
  and the existing merge gate (adjudication of findings before merge still applies).
- The sweeper resolves only OCR's own threads: a human who agrees with a lingering thread
  must still resolve or reply to it themselves — human engagement always wins.
- +1 LLM round-trip per lingering thread per run; a PR left unattended with 25 stale
  threads pays 25 calls per push.
