---
id: 20261007-1919-default-branch-is-protected-pr-only-no-force-pus
title: Default branch is protected; PR-only, no force push
kind: preference
topics: [git, workflow, branch-protection, enforcement]
projects: [cms-system, personal-site, njeremoto-operations, hivemind, dotfiles]
origin: gift
posted: 2026-10-07T19:19+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The old rule was "never commit". Stated absolutely, that had gone stale — it left the
protection resting on every agent remembering it, in every repo, forever. A rule that
lives only in an instruction file is one careless session away from being broken.

## What we decided

**Every repository enforces its own protection. The default branch is not writable.**

```
  PATCH /repos/{owner}/{repo}/branches/{default}/protection
    required_pull_request_reviews.required_approving_review_count : 0
    enforce_admins                                              : true
    allow_force_pushes                                          : false
    allow_deletions                                             : false
    restrictions                                                : null (nobody, not even admins)

  PATCH /repos/{owner}/{repo}
    allow_rebase_merge  : true
    allow_merge_commit  : false
    allow_squash_merge  : false
```

- No direct push to the default branch. Ever.
- No force push, no branch deletion — not even by a repo admin. `enforce_admins: true`
  is what makes this real; without it an admin bypasses protection entirely.
- Every change arrives as a pull request.
- Approving review count is **0**, deliberately: this is a solo + AI workflow, and
  requiring one human approval would deadlock it. The PR requirement is the control.

## Why

Move the rule out of the agent's memory and into the platform. Enforcement the agent
cannot forget is worth more than a rule the agent honours.

## The cost

Legitimate hotfixes need the same PR ceremony as everything else, and a compromised
admin token can still disable protection — this raises the bar, it does not make pushes
impossible. Note that `enforce_admins` applies to you too; that is the point.
