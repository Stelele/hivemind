---
id: 20261114-0720-repository-baseline-restated-squash-merges-allow
title: Repository baseline restated: squash merges allowed, protection unchanged (withdraws the stale 0049/0054 squash lines)
kind: decision
topics: [workflow, github]
projects: [hivemind]
origin: gift
posted: 2026-11-14T07:20+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Ratifying ADR 0055 (squash merges enabled account-wide) exposed that two LIVE core
sections still prescribe the old posture: ADR 0049's "Default branch is protected;
PR-only, no force push" and ADR 0054's "Repository baseline" both carry
`allow_squash_merge : false` in their PATCH blocks. Flagged in the
20261114-0650 question post; the owner authorized the core update this session.

## What we decided

The repository baseline is restated as one current section (this ADR). Everything the
two superseded sections enforced is preserved verbatim except the merge-methods line,
which now matches ADR 0055:

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
    allow_squash_merge  : true           # ADR 0055: one commit per merge; rebase selectable
```

Two separate settings, two separate jobs — do not confuse them:

| Setting | Governs |
|---|---|
| `delete_branch_on_merge` | a merged PR's **head branch** disappears automatically |
| `allow_deletions: false` | nobody may delete the **default branch** |

Enabling auto-delete does not weaken default-branch protection (verified on `camera-nvr`
with both live simultaneously). Free-tier repos cannot protect their default branch at
all — that remains a documented exception, not a silent hole. Verify with:

```
  gh api repos/$REPO -q .delete_branch_on_merge                                 # true
  gh api repos/$REPO/branches/$DEFAULT/protection -q .enforce_admins.enabled    # true
  gh api repos/$REPO -q .allow_squash_merge                                     # true
```

A 403 "Upgrade to GitHub Pro" on the protection call is a finding, not a pass. The two
superseded sections (0049's, 0054's) move to `archive/` with their historical PATCH
blocks intact; ADR 0049 and 0054 remain in `decisions/` as the reasoning of record.

## Why

The merge-methods line lived in two baseline sections and went stale the moment ADR 0055
landed — an agent obeying either PATCH block literally would re-disable squash
account-wide, silently undoing the owner's decision. Restating the baseline as a single
current section (and superseding the two stale ones citing this ADR) keeps every core
invariant: text-to-ADR correspondence, INDEX routing, no hand edits.

## The cost

- The archived sections' historical PATCH blocks (with squash=false) are out of INDEX
  routing — recovering any nuance they carried means reading `archive/workflow.md`.
- Agents citing "ADR 0049/0054" from memory still reference the old numbers; the ADR
  files remain as history but the live text is here.
- Merge-method changes now edit this section via the same supersede-and-restatement
  cycle rather than two places.
