---
id: 20261104-1537-review-gate-is-opencodereview-and-private-repos
title: Review gate is OpenCodeReview, and private repos meter every Actions minute
kind: lesson
topics: [ci/tools, review]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-04T15:37+02:00
endorsements: 0
status: promoted
promoted-to: core/workflow.md#review-gate-is-opencodereview-and-private-repos
supersedes: -
---
Decision from 2026-11-04: CodeRabbit is gone from every Stelele repo, and the standing review gate plus an Actions-minutes economy rule take its place.

## The rule

**The review gate is OpenCodeReview (ocr), and Actions minutes are metered on private repos.**

1. Every PR is reviewed by `ocr-review` (alibaba/open-code-review v1.13.5, glm-5.3-flash through the OpenCode Go subscription - `$10/mo` for far more than CodeRabbit's included quota). OCR's findings are adjudicated before merge: fix them, or reply on the PR explaining why they do not apply. Model churn is real - it reversed its own round-1 style suggestion in round 3 of one PR - so rebuttal-on-thread is a first-class move.
2. Private repos share the 2,000 free Actions-minutes/month pool; public repos are unmetered. On private repos:
   - Verify locally first (local test suites, local `ocr review` - it uses the Go subscription, not Actions).
   - Tag housekeeping/rollout commits `[skip ci]` so opening and rebase-merging them fires nothing.
   - Cancel duplicate review runs immediately (a second bot reviewing the same diff is wasted minutes).
   - Deliberate CI (full test suite + e2e) is the merge gate, fired once, on purpose.
3. OCR runs locally as `ocr review --from <base> --to <branch>` with OpenCode as host only in delegation mode; for direct use configure the custom provider `go` (`https://opencode.ai/inference/go/openai/v1`, `glm-5.3-flash`) and provider-level `extra_headers` `x-opencode-session=<id>` - the top-level `llm.extra_headers` config is silently ignored on real requests.

Secrets: OCR_LLM_URL / OCR_LLM_TOKEN / OCR_LLM_MODEL seeded on all 100 repos by `~/.local/bin/stelele-ocr-secrets.sh`; a Go key rotation silently breaks review CI repo-wide until that script is re-run. Public-repo caveat: Go review minutes are not billed against Actions, but the Go allowance itself is shared.

## The cost

- ocr reviews meter the Go allowance, not Actions - spend moves from a monthly-minute pool to a token one, and a fast model still takes ~30 runner-minutes for a 50-file diff (~1.5% of a private repo's monthly pool per review if run on Actions instead of locally).
- `[skip ci]` commits skip the merge gate too, so a merge can land without fresh CI if nobody fires it deliberately. The one deliberate CI run before merging private-repo PRs is the compensating control - it is a rule, not a preference.
- Third-party GitHub Apps cannot be uninstalled via PAT (403); CodeRabbit's App needs one manual removal at github.com/settings/installations.
- Locally-run ocr reviews are invisible in PR timelines; their findings live in session files only, so the adjudication record is the commit messages and the PR thread, not the PR's review history.
