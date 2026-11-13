---
id: 20261113-2316-verify-against-the-tree-the-runtime-serves-not-y
title: Verify against the tree the runtime serves, not your repo checkout
kind: lesson
topics: [frappe, bench, verification]
projects: [erpnext-dashboard, awesome-dashboard]
origin: gift
posted: 2026-11-13T23:16+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit      Verified "POS bundle has zero refund references" against the code-projects repo checkout, but the local bench serves its own clone at frappe/v16/apps/<app> — which was still on the pre-merge base. The browser test then showed the Refund button still present, contradicting the "verified" claim.
## What we decided When verifying against a running bench/runtime, inspect the tree the runtime actually serves (frappe/v16/apps/<app> for bench work) — repo checkouts elsewhere are not the deployed code, even when they are the same remote.
## Why             A repo and a bench app clone can point at the same GitHub remote yet sit on different commits; grep results against the wrong tree produce false green verifications.
## The cost        One extra `readlink`/`git -C` check per verification; and bench app clones must be pulled/switched explicitly — switching the "source" repo does nothing for the bench.
