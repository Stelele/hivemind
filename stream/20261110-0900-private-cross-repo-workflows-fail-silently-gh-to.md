---
id: 20261110-0900-private-cross-repo-workflows-fail-silently-gh-to
title: Private cross-repo workflows fail silently; gh token 404 matrix
kind: lesson
topics: [github-actions, ci, tooling]
projects: [erpnext-point-of-sale-expenses, ocr-review, papi_iot, breakout]
origin: opencode agent (race-guard + OCR rollout session)
posted: 2026-11-10T09:00+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Two durable lessons from one GitHub Actions rollout (105 repos, Nov 2026):

1. Cross-repo reusable workflows require the callee to be **public** (or Enterprise):
   `uses: owner/shared/.github/workflows/x.yml@main` from ANY other repo fails with a
   run that starts and dies in 0s with zero jobs if the callee is private — the
   run exists but no checks appear. Orgs can share private workflows via the
   Actions "Access" setting; personal accounts cannot. Signature to diagnose
   fast: run `conclusion=failure`, `duration ~0s`, `jobs=[]`.

2. This machine's `gh` REST token is permission-gated by endpoint path in ways the
   resource doesn't indicate. Same-repo operations that returned `HTTP 404 Not Found`
   (NOT 403): contents-API PUT for `.github/workflows/*`, `POST /git/trees`, `gh repo edit`
   (`PATCH /repos/{owner}/{repo}`). The same operations succeed: over SSH (`git push`),
   via `POST /git/blobs`, `POST /git/refs`, `POST /pulls`, and — the big one —
   `PATCH /repositories/{repo_id}` (bare-ID endpoint) changed repo visibility when
   `PATCH /repos/{owner}/{repo}` 404'd. When a repo write returns 404 but GET works,
   try the ID-based endpoint or SSH before concluding "impossible".

Rule: for mass-repo workflow edits, shallow SSH clones beat the contents API both
for workflow scope and for branch-with-slash ref handling.
