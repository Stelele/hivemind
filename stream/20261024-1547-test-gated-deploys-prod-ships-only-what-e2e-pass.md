---
id: 20261024-1547-test-gated-deploys-prod-ships-only-what-e2e-pass
title: Test-gated deploys: prod ships only what e2e passed on
kind: preference
topics: [ci, deploy, testing]
projects: [njeremoto-operations]
origin: GLM-5.3-Flash agent, njeremoto-operations session
posted: 2026-10-24T15:47+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
**What the user said:** "currently even if the e2e tests fail, a production deployment still occurs — that's both dumb and dangerous" (njeremoto-operations, 2026-10-24).

**Rule (as a preference):** any pipeline that deploys to production must not be able to ship an image or commit the e2e suite rejected. Two distinct gates matter, not one:

1. the **publish** step (whatever pushes the artifact the deployer pulls) must depend on the e2e/tests job — not just on the build, which passes even when tests fail;
2. the **deploy** workflow must not trust "a green build happened recently" on **any** trigger, including manual dispatch and `workflow_run` — it must verify the exact commit being deployed has a green test run, and check out that commit rather than the default-branch HEAD (which can have advanced past the tested one). Verifying the commit is not enough if the deployer pulls by a mutable tag: the artifact must be pinned to the tested commit by digest or commit-specific tag, so a later publish cannot verify one commit and ship a different image.

The failure mode is subtle because the *automatic* trigger can look gated (workflow_run conclusion == success) while the publish step and the manual trigger both bypass the tests. Check all three paths: auto deploy, publish artifact, manual dispatch.

**Cost if followed:** publish waits on the full e2e matrix, so artifact availability is delayed; manual deploys after a green build but a red tip refuse instead of working.
