---
id: 20261103-2242-replace-coderabbit-with-opencodereview-across-st
title: Replace CodeRabbit with OpenCodeReview across Stelele repos (ADR 0051 successor)
kind: lesson
topics: [ci/tools, review]
projects: [njeremoto-operations, cms-system, erpnext-dashboard]
origin: gift
posted: 2026-11-03T22:42+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
On 2026-11-03 the user decided to remove CodeRabbit from all Stelele repos and standardize on OpenCodeReview (ocr / alibaba/open-code-review) for AI PR review, driven by: free/BYOK (OpenCode Go subscription, glm-5.3-flash), OCR's deterministic file-selection architecture, no per-repo rate-limit cliff.

Mechanics worth keeping:

- Review gate replacement: the ocr-review workflow (pinned composite action, OCR_LLM_* repo secrets seeded across all repos via stelele-ocr-secrets.sh). Pilot PR #39 in njeremoto-operations merged after three rounds of add's findings were fixed or rebutted; final round surfaced zero findings.
- CodeRabbit config files (.coderabbit.yaml) existed in frappe-self-host and class-booking-system; removal PRs opened. The GitHub App itself CANNOT be uninstalled via user PAT (403 - requires app-facing auth); the owner must visit github.com/settings/installations once.
- Successor rule to ADR 0051: adjudicate the configured review bot's (OCR's) comments before merging - fix them or reply on the PR. Same discipline, different reviewer. glm-5.3-flash cycles low-severity re-findings on re-runs (it reversed its own round-1 style suggestion in round 3), so rebuttal-on-thread is a real, used path.

## The cost

- Reviews now metered against the OpenCode Go allowance instead of CodeRabbit's included quota; a Go key rotation silently breaks CI review in every repo until stelele-ocr-secrets.sh is re-run (no expiry alert from GitHub).
- Uninstall of the App is manual, so both bots could review the same PR during the transition window if install lingers.
- OCR's multi-round review cycles provide diminishing returns on tiny PRs; adjudicate and merge rather than looping until zero findings for cosmetic nits.
