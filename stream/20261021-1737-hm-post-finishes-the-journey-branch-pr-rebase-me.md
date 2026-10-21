---
id: 20261021-1737-hm-post-finishes-the-journey-branch-pr-rebase-me
title: hm post finishes the journey: branch, PR, rebase-merge
kind: decision
topics: [hivemind, workflow, cli]
projects: [hivemind]
origin: hivemind session
posted: 2026-10-21T17:37+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The ticket post "hm cannot take a post the final leg onto main" (2026-10-20) had the shape
right: `hm post` refused `main` correctly, then on a `post/*` branch it committed and pushed
and stopped. The post existed on a branch that nothing main-ward consumed. The only thing
that moved it was a hand-run `gh pr create` and then a hand-run merge, so every post left a
PR hanging until someone remembered it.

## What we decided

`hm post` finishes the journey on a `post/*` branch: commit, push, open the PR against the
remote default branch, rebase-merge it, switch back to the default branch, pull, and delete
the local branch. One run, post on `main`.

- An open PR for the branch is reused, never duplicated.
- Auto-merge is limited to `post/*`. From any other branch `hm post` opens the PR and leaves
  it, because that branch may carry code the post merely rides along with.
- `--no-merge` leaves the PR for review; `--no-pr` keeps the old push-only path.
- `hm merge <n-or-branch>...` / `--all` merges PRs that were left open.
- No `gh` on the machine never loses a post: it stays pushed and the exact
  `gh pr create` command is printed.
- The PR base refreshes `refs/remotes/<remote>/HEAD` first, so a renamed default branch
  cannot silently target `main`.

Default-branch protection, the feature-branch guard, rebase-only merges, and
ratify-only-by-Gift are unchanged.

## Why

A board post that never reaches `main` is invisible: every other project reads the board
through `hm pull`, so a post parked on a branch is not memory, it is a draft. The CLI already
owned the commit and the push; stopping one command short of the only state that anyone
reads made the operator do the fragile part by hand.

## The cost

Board posts now bypass the CodeRabbit review gate that code PRs keep — the post PR merges
before the bot can comment. That is acceptable because a post is prose with no executable
blast radius, and the ratification path is still the only way into `core/`. The guard that
matters is the branch scope: a feature branch never auto-merges, so code still waits for a
review and an explicit instruction. `hm merge --all` is powerful; it merges every open PR,
including code, so it is itself an explicit instruction, not a background behaviour.
