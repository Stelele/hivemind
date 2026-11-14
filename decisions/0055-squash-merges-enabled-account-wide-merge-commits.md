# 0055. Squash merges enabled account-wide; merge commits off
**Status:** accepted
**Date:** 2026-11-14
**Affects:** hivemind, cms-system, erpnext-dashboard

## Context

ADR 0050 disabled squash deliberately and offered the out: "If you would rather keep
squash available for PRs that accumulate noisy fixups, say so and this ADR gets
superseded." The owner has now said so. Also found while sweeping: 94 of 110 repos still
allowed merge commits, contradicting the same baseline.

The owner's goal is "basically one commit after merging the PR" — squash is exactly that.
Multi-commit PRs (fixup accumulation, agent churn) land as a single clean commit instead of
each fixup landing verbatim on the default branch. ADR 0050's tidy-branch cost assumed
rebase-merges; squash removes the burden of pre-merge amending instead of paying it.

## Decision

Squash merges are now enabled on every Stelele repo; merge commits are disabled everywhere;
rebase stays enabled. All 110 repos verified uniform: squash=true, rebase=true,
mergecommit=false.

## Consequences

- Squashed merges lose the one-logical-change-per-commit boundaries ADR 0006 establishes
  inside the squashed commit — the history shows one commit where five logical changes were
  made. Commit messages inside the PR become invisible to `git log`.
- The default-branch rule "every commit is one logical change" (ADR 0006) now holds only
  until merge time; after a squash it holds per-PR, not per-commit.
- No regression on safety: default-branch protection (ADR 0049/0054) is untouched, and
  squash is selectable, not mandatory — rebase merges remain available.
