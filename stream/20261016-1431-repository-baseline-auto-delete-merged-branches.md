---
id: 20261016-1431-repository-baseline-auto-delete-merged-branches
title: Repository baseline: auto-delete merged branches, and protect every default branch
kind: decision
topics: [workflow]
projects: [hivemind, njeremoto-operations, camera-nvr]
origin: gift
posted: 2026-10-16T14:31+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Twelve repos got the ADR 0052 docs change merged, each leaving a
`chore/adr-0052-free-branch-commits` branch behind. Deleting them by hand is
per-repo busywork, and it does not scale — every future merged PR leaves the
same residue.

The instinct is to enable `delete_branch_on_merge` everywhere and be done. That is
right, but on its own it is a *setting*, not a *rule*: nothing tells the next agent
or the next person that this repo is configured that way, and nothing records why.

Meanwhile some repos in the same sweep turned out to be **unprotected**:
`njeremoto-operations` reports `403 Upgrade to GitHub Pro or make this repository
public` for branch protection, and `hivemind` returns `404 Branch not protected`.
Neither enforces ADR 0049 at the platform level. The rule says every repo protects
its own default branch. Two repos quietly do not.

## What we decided

**Repository baseline — apply to every repo, checked not assumed.**

```
  PATCH /repos/{owner}/{repo}
    delete_branch_on_merge : true        # merged PR branches clean themselves up

  PATCH /repos/{owner}/{repo}/branches/{default}/protection
    required_pull_request_reviews.required_approving_review_count : 0
    enforce_admins                                              : true
    allow_force_pushes                                          : false
    allow_deletions                                             : false
    restrictions                                                : null

  PATCH /repos/{owner}/{repo}
    allow_rebase_merge  : true
    allow_merge_commit  : false
    allow_squash_merge  : false
```

Two separate settings, two separate jobs — do not confuse them:

| Setting | Governs |
|---|---|
| `delete_branch_on_merge` | a merged PR's **head branch** disappears automatically |
| `allow_deletions: false` | nobody may delete the **default branch** |

Enabling auto-delete does **not** weaken default-branch protection. Verified on
`camera-nvr` with both live simultaneously: `delete_branch_on_merge=true` alongside
`allow_force_pushes.enabled=false`, `allow_deletions.enabled=false`,
`enforce_admins.enabled=true`.

**Free tier repos cannot protect their default branch at all** — protection is a Pro
feature. For those, ADR 0049's platform enforcement is unavailable and the
default branch is protected only by agent discipline. Say so explicitly rather than
reporting those repos as compliant.

## Why

A rule that lives only in a setting is one repo-creation away from gone, which is the
same failure ADR 0049 diagnosed about rules that live only in instruction files —
just moved one layer down. Recording the baseline makes the expected posture
checkable, and makes "this repo has no protection because it is on the free tier" a
known, accepted exception instead of a silent hole.

Auto-delete earns its place on its own: it removes a repetitive manual step and the
stale branches it creates are exactly the ones that confuse a later agent about
what is still in flight.

## The cost

- A merged PR's branch is gone from the remote immediately, so recovering it means
  re-fetching from the merge ref, not from the branch. Keep the PR link.
- Force-push permission to a feature branch is a separate matter from deleting it —
  auto-delete does not grant force-push, and does not restrict it either.
- Private repos on the free tier cannot satisfy this baseline at all. Either upgrade
  or accept the exception in writing.

## Verify

```bash
gh api repos/$REPO -q .delete_branch_on_merge                    # true
gh api repos/$REPO/branches/$DEFAULT/protection -q .enforce_admins.enabled   # true
```

A `403 Upgrade to GitHub Pro` on the protection call is a **finding**, not a
pass — record it as an exception.
