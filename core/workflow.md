# Workflow — git, commits, CI, verification

## Never commit, push, or open a PR without an explicit instruction

> **Superseded by [ADR 0049](../decisions/0049-default-branch-is-protected-pr-only-no-force-pus.md).**
> Protection now lives in the repository itself rather than in agent memory. The
> agent-side half of this rule is retained and still applies — see below.

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

## Batch the change, then test once

Make the whole set of edits, then run the tests. Do not run the suite after each
individual edit — on anything non-trivial it is a waste of wall-clock, and that time is
real developer time.

*Evidence: 2026-05-27 — "don't run tests on every change, its too slow, do all your
changes in one go then test afterwards."*
→ [ADR 0002](../decisions/0002-batch-the-change-then-test-once.md)

## Keep CI under ten minutes

If a change pushes the pipeline past ~10 minutes, that is a regression worth fixing in the
same change. Slow pipelines waste developer time waiting.

*Evidence: 2026-09-08 — "I want the entire ci pipeline to run in under 10 mins. currently
too much developer time is wasted waiting for the pipeline to finish."*
→ [ADR 0003](../decisions/0003-keep-ci-under-ten-minutes.md)

## Defer rather than expand

When a feature's scope is already large, take the smaller option and file the rest under
future development. Say so out loud so the deferral is on record.

*Evidence: 2026-05-24 — "lets go with A for now since the scope is already pretty big and
file this under future development."*
→ [ADR 0004](../decisions/0004-defer-rather-than-expand.md)

## Chain the setup scripts, and end with one verifier

Multi-step environment setup ships as a chain that runs in order, plus a final script that
verifies the whole setup is correct. Manual per-step invocation is a defect.

*Evidence: 2026-07-23 — "I'd prefer these scripts to be chained. its kinda a pain that I
would need to run them manually. I'd also like a final script that verifys everything is
set up correctly."*
→ [ADR 0005](../decisions/0005-chain-setup-scripts-and-end-with-a-verifier.md)

## Commit message style

Inferred, **not yet confirmed** — see the note in
[`workflow.md` provenance](https://github.com/Stelele/hivemind). Conventional-Commit
prefixes (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`) with a short
imperative subject. One logical change per commit. Body only when the *why* is not obvious
from the subject.
→ [ADR 0006](../decisions/0006-conventional-commit-subjects-one-change-per-commit.md)

## Keep fixer prompts to 8 edits or fewer

### What I hit

Fixer agents were hitting step limits on batches of 10 or more edits.

### What we decided

Keep fixer prompts to **8 edits or fewer**, and quote the exact string to replace. Longer
batches exhaust the agent's step budget mid-fix.

### Why

Step budget scales with the number of distinct decisions in the prompt, not the number of
lines. Exact strings remove the re-reading that inflates it.

### The cost

More, smaller dispatches. Batch by concern rather than by file count.

## Reviewer line numbers go stale

### What I hit

Reviewer reports referenced line numbers that no longer matched the file after intervening
edits, so applying their suggestions corrupted the source.

### What we decided

Always adjudicate a review against the **current** source before applying anything. Check
that the target line still contains the content the reviewer described.

### Why

Reviewers reason over a snapshot. By the time you act, that snapshot is stale — especially
in a multi-agent loop where a fixer has already edited the region.

### The cost

An extra verification step per finding. Skipping it means the reviewer becomes a source
of bugs rather than a source of fixes.

## Default branch is protected; PR-only, no force push

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

## Rebase merges only; linear history

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

## Address CodeRabbit comments before claiming done

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

## Agents commit freely to feature branches; the default branch stays PR-only

### What I hit

ADR 0001 — "never commit without an explicit instruction" — was superseded by ADR 0049 on
2026-10-07. It is still quoted as a live rule in 18 places: `core/workflow.md`, the global
`~/.config/opencode/AGENTS.md`, `hivemind/AGENTS.md`, and 16 project `AGENTS.md` files, all
citing it by number.

Meanwhile the part of it that still bites is pure ceremony. With the default branch
platform-protected, an agent asking "may I commit?" before touching a throwaway feature
branch is asking permission for something that cannot reach `main` and cannot be undone
silently.

The rule that was supposed to protect work had become a prompt, not a control.

### What we decided

**Agents commit and push freely to non-default branches. The default branch stays PR-only.**

- **Free, no permission needed:** `git commit`, `git push` to any branch that is not the
  default branch, `git branch`, `git rebase`, amending one's own commits, force-pushing a
  feature branch nobody else is using.
- **Still requires an explicit instruction:** pushing or committing to the default branch
  (blocked by platform protection anyway), and **merging** a PR into the default branch.
- Applies to you **and to every subagent dispatched**. The old "pass the no-commit
  instruction down" step is deleted; do not pass any restriction down with it.

The review gate moves from "the agent asks before it writes" to "the default branch requires
a pull request". Both are gates; only one of them cannot be forgotten.

### Why

ADR 0049 already made this argument for the default branch: *a rule that lives only in an
instruction file is one careless session away from being broken.* The same argument applies
to the agent-side half, and it has now demonstrably decayed — 18 files still cite a
superseded ADR as though it were current. Extending the platform-enforced posture to
commits on feature branches keeps one gate instead of two, and drops the one that rotted.

Feature-branch pushes are also visible and cheap to undo. The irreversible step is the merge
into the default branch, and that is exactly where the control belongs.

### The cost

- A PR is now the first place a change is *seen*, rather than the working tree. Long-running
  branches accumulate commits nobody has looked at; batching your own amendments locally
  before pushing matters more (compounds ADR 0050, rebase-only merges).
- Force-pushing a feature branch is permitted. If two agents share a branch, one can clobber
  the other. Keep agent-per-branch.
- Nothing stops an agent from committing straight to a feature branch that the user never
  asked for. Garbage branches are cheap to delete; garbage on `main` is not, and that is the
  case the platform still refuses.
- This weakens the ADR 0001 evidence base — the user originally disliked unprompted commits
  enough to say so five times across three projects. That preference is being deliberately
  reversed, not quietly outvoted. If the ceremony turns out to matter after all, this ADR
  gets superseded.
