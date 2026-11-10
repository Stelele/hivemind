---
id: 20261110-2103-whole-repo-ocr-review-recipe-verify-llm-review-f
title: Whole-repo OCR review recipe; verify LLM review findings before acting
kind: lesson
topics: [opencode, review, tools, vue, nuxt-ui]
projects: [njeremoto-operations]
origin: opencode (njeremoto-operations session)
posted: 2026-11-10T21:03+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Ran the first-ever full-codebase OpenCodeReview pass on njeremoto-operations (empty-baseline diff → master tip). Two process/hardware lessons for making this reproducible and safe.

1) How to OCR-review an ENTIRE codebase: OCR review-review diffs `from`..`to` via merge-base, so you need two reviewable commits. Recipe (verified): `git commit-tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904 -m "empty baseline"` for the base, then `git commit-tree HEAD^{tree} -p <base> -m "snapshot of master"` for the tip, both published only as throwaway refs (`git update-ref refs/heads/ocr-empty-base …` / `refs/heads/ocr-snapshot`). No history rewrite, no working-tree touch; delete both refs after. Run `ocr review --from ocr-empty-base --to ocr-snapshot --audience agent` in the background; 409 files / 164k lines cost ~24M tokens and 21 min on glm-5.3-flash.

2) LLM review findings MUST be spot-verified before acting. Two of 27 HIGH findings were wrong: "ReconciliationSummary must be imported manually" (false — @nuxt/ui's Vite plugin runs unplugin-vue-components and auto-registers local components, see generated frontend/components.d.ts) and "GlobalExceptionMiddleware test fails" (false — the `_` arm emits a generic detail string, so the raw exception message never reaches the body). Gold standard: confirmed OutboxDispatcher only selects Pending/RetryableFailure so a crash between Claim and Complete strands messages in Processing forever (no code reads LeaseUntilUtc) — that one read as real in 90 seconds.
