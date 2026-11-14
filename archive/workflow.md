<!-- Superseded rules, kept for the record. core/ holds only live rules. -->

## Never commit, push, or open a PR without an explicit instruction

**Withdrawn** 2026-10-19 by [ADR 0052-agents-commit-freely-to-feature-branches-the-def.md](../decisions/0052-agents-commit-freely-to-feature-branches-the-def.md).

ADR 0049 withdrew the branch half on 2026-10-07; ADR 0052 withdrew the agent-side half on 2026-10-16. Current rule: commit and push to feature branches freely — merging into the default branch still needs an explicit instruction.

> **Superseded by [ADR 0049](../decisions/0049-default-branch-is-protected-pr-only-no-force-pus.md),
> then by [ADR 0052](../decisions/0052-agents-commit-freely-to-feature-branches-the-def.md).**
> Protection now lives in the repository itself rather than in agent memory, and the
> agent-side half of this rule is **withdrawn** — see
> [Agents commit freely to feature branches](../core/workflow.md#agents-commit-freely-to-feature-branches-the-default-branch-stays-pr-only).
>
> **Current rule:** commit and push to feature branches freely; the default branch and any
> merge into it still need an explicit instruction.
>
> The text below is kept for history only. Do not follow it.

Do not commit. Do not push. Do not open a PR. Not even a "safe" small one. Not even when
a subagent finished the work cleanly. Leave the change in the working tree and say what
you did.

This applies to you **and to every subagent you dispatch**. If you hand work to a subagent,
the no-commit instruction goes in the prompt.

*Evidence: 2026-06-05 — "I don't like it when you automatically commit code either by you
or your subagents when you do changes. I like to see everything thats written and give
reviews." Repeated unprompted across cms-system, personal-site and erpnext-dashboard.*
→ [ADR 0001](../decisions/0001-never-commit-without-an-explicit-instruction.md)
*(superseded 2026-10-07 by ADR 0049)*

## Address CodeRabbit comments before claiming done

**Withdrawn** 2026-11-04 by [ADR 0054-review-gate-is-opencodereview-and-private-repos.md](../decisions/0054-review-gate-is-opencodereview-and-private-repos.md).

Reviewer replaced: CodeRabbit removed from all repos; the gate is now OCR findings and the ADR 0054 minutes-economy rule

### What I hit

Work was being declared done while review comments sat unaddressed on the PR.

### What we decided

**Address CodeRabbit's comments before claiming the work is done.**

Before declaring done:

1. Read the PR's review comments.
2. If CodeRabbit's rate limit is **not** exhausted and there are comments, address
   every one of them — fix it, or reply explaining why it does not apply.
3. If the rate limit **is** exhausted, or no comments were produced, say so explicitly
   and the rule is satisfied.
4. An unaddressed comment is not done. Not "done except for the nits".

```bash
gh pr view <n> --comments
gh pr checks <n>          # surfaces the rate-limit / no-review case
```

### Why

The review bot is the only reviewer on a solo-plus-AI repo. If its output is collected
but never read, the automation is theatre and you find out about it in production.

### The cost

Extra turns per PR, and some comments will be wrong. Disagreement is allowed — but it
has to be argued in a reply on the PR, not silently ignored.

## Rebase merges only; linear history

**Withdrawn** 2026-11-14 by [ADR 0055-squash-merges-enabled-account-wide-merge-commits.md](../decisions/0055-squash-merges-enabled-account-wide-merge-commits.md).

Owner chose squash-merge availability account-wide: one commit after merge; rebase stays selectable

### What I hit

Merge commits were accumulating noise in otherwise linear histories.

### What we decided

**Rebase merges only.** Disable merge commits *and* squash; leave rebase enabled.

```
allow_rebase_merge: true
allow_merge_commit: false
allow_squash_merge: false
```

### Why

The repo already commits one logical change per commit (ADR 0006), so rebase preserves
exactly the history you meant to write. Squash would re-flatten those commits and throw
away the boundaries; merge commits add a commit per PR that says nothing.

### The cost

You must keep PR branches tidy — every commit on a PR branch lands on the default
branch as-is. A PR with fixup commits lands as fixup commits. Batching your own
amendments locally before pushing is now part of the workflow.

Squash is off deliberately. If you would rather keep squash available for PRs that
accumulate noisy fixups, say so and this ADR gets superseded.

## Default branch is protected; PR-only, no force push

**Withdrawn** 2026-11-14 by [ADR 0058-repository-baseline-restated-squash-merges-allow.md](../decisions/0058-repository-baseline-restated-squash-merges-allow.md).

Restated by ADR 0058 with squash merges allowed; protection content preserved verbatim

### What I hit

The old rule was "never commit". Stated absolutely, that had gone stale — it left the
protection resting on every agent remembering it, in every repo, forever. A rule that
lives only in an instruction file is one careless session away from being broken.

### What we decided

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

### Why

Move the rule out of the agent's memory and into the platform. Enforcement the agent
cannot forget is worth more than a rule the agent honours.

### The cost

Legitimate hotfixes need the same PR ceremony as everything else, and a compromised
admin token can still disable protection — this raises the bar, it does not make pushes
impossible. Note that `enforce_admins` applies to you too; that is the point.
