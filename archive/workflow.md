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

## Repository baseline: auto-delete merged branches, and protect every default branch

**Withdrawn** 2026-11-14 by [ADR 0058-repository-baseline-restated-squash-merges-allow.md](../decisions/0058-repository-baseline-restated-squash-merges-allow.md).

Restated by ADR 0058 with squash merges allowed; baseline content preserved verbatim

### What I hit

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

### What we decided

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

### Why

A rule that lives only in a setting is one repo-creation away from gone, which is the
same failure ADR 0049 diagnosed about rules that live only in instruction files —
just moved one layer down. Recording the baseline makes the expected posture
checkable, and makes "this repo has no protection because it is on the free tier" a
known, accepted exception instead of a silent hole.

Auto-delete earns its place on its own: it removes a repetitive manual step and the
stale branches it creates are exactly the ones that confuse a later agent about
what is still in flight.

### The cost

- A merged PR's branch is gone from the remote immediately, so recovering it means
  re-fetching from the merge ref, not from the branch. Keep the PR link.
- Force-push permission to a feature branch is a separate matter from deleting it —
  auto-delete does not grant force-push, and does not restrict it either.
- Private repos on the free tier cannot satisfy this baseline at all. Either upgrade
  or accept the exception in writing.

### Verify

```bash
gh api repos/$REPO -q .delete_branch_on_merge                    # true
gh api repos/$REPO/branches/$DEFAULT/protection -q .enforce_admins.enabled   # true
```

A `403 Upgrade to GitHub Pro` on the protection call is a **finding**, not a
pass — record it as an exception.
