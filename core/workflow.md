# Workflow — git, commits, CI, verification

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

## Repository baseline: auto-delete merged branches, and protect every default branch

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

## Review gate is OpenCodeReview, and private repos meter every Actions minute

Decision from 2026-11-04: CodeRabbit is gone from every Stelele repo, and the standing review gate plus an Actions-minutes economy rule take its place.

### The rule

**The review gate is OpenCodeReview (ocr), and Actions minutes are metered on private repos.**

1. Every PR is reviewed by `ocr-review` (alibaba/open-code-review v1.13.5, glm-5.3-flash through the OpenCode Go subscription - `$10/mo` for far more than CodeRabbit's included quota). OCR's findings are adjudicated before merge: fix them, or reply on the PR explaining why they do not apply. Model churn is real - it reversed its own round-1 style suggestion in round 3 of one PR - so rebuttal-on-thread is a first-class move.
2. Private repos share the 2,000 free Actions-minutes/month pool; public repos are unmetered. On private repos:
   - Verify locally first (local test suites, local `ocr review` - it uses the Go subscription, not Actions).
   - Tag housekeeping/rollout commits `[skip ci]` so opening and rebase-merging them fires nothing.
   - Cancel duplicate review runs immediately (a second bot reviewing the same diff is wasted minutes).
   - Deliberate CI (full test suite + e2e) is the merge gate, fired once, on purpose.
3. OCR runs locally as `ocr review --from <base> --to <branch>` with OpenCode as host only in delegation mode; for direct use configure the custom provider `go` (`https://opencode.ai/inference/go/openai/v1`, `glm-5.3-flash`) and provider-level `extra_headers` `x-opencode-session=<id>` - the top-level `llm.extra_headers` config is silently ignored on real requests.

Secrets: OCR_LLM_URL / OCR_LLM_TOKEN / OCR_LLM_MODEL seeded on all 100 repos by `~/.local/bin/stelele-ocr-secrets.sh`; a Go key rotation silently breaks review CI repo-wide until that script is re-run. Public-repo caveat: Go review minutes are not billed against Actions, but the Go allowance itself is shared.

### The cost

- ocr reviews meter the Go allowance, not Actions - spend moves from a monthly-minute pool to a token one, and a fast model still takes ~30 runner-minutes for a 50-file diff (~1.5% of a private repo's monthly pool per review if run on Actions instead of locally).
- `[skip ci]` commits skip the merge gate too, so a merge can land without fresh CI if nobody fires it deliberately. The one deliberate CI run before merging private-repo PRs is the compensating control - it is a rule, not a preference.
- Third-party GitHub Apps cannot be uninstalled via PAT (403); CodeRabbit's App needs one manual removal at github.com/settings/installations.
- Locally-run ocr reviews are invisible in PR timelines; their findings live in session files only, so the adjudication record is the commit messages and the PR thread, not the PR's review history.

## Squash merges enabled account-wide; merge commits off

### What I hit

ADR 0050 disabled squash deliberately and offered the out: "If you would rather keep
squash available for PRs that accumulate noisy fixups, say so and this ADR gets
superseded." The owner has now said so. Also found while sweeping: 94 of 110 repos still
allowed merge commits, contradicting the same baseline.

### What we decided

Squash merges are now enabled on every Stelele repo; merge commits are disabled everywhere;
rebase stays enabled. All 110 repos verified uniform: squash=true, rebase=true,
mergecommit=false.

### Why

The owner's goal is "basically one commit after merging the PR" — squash is exactly that.
Multi-commit PRs (fixup accumulation, agent churn) land as a single clean commit instead of
each fixup landing verbatim on the default branch. ADR 0050's tidy-branch cost assumed
rebase-merges; squash removes the burden of pre-merge amending instead of paying it.

### The cost

- Squashed merges lose the one-logical-change-per-commit boundaries ADR 0006 establishes
  inside the squashed commit — the history shows one commit where five logical changes were
  made. Commit messages inside the PR become invisible to `git log`.
- The default-branch rule "every commit is one logical change" (ADR 0006) now holds only
  until merge time; after a squash it holds per-PR, not per-commit.
- No regression on safety: default-branch protection (ADR 0049/0054) is untouched, and
  squash is selectable, not mandatory — rebase merges remain available.

## OCR verdict sweeper: in-place fixes now auto-resolved; resolve_outdated only sees line deletions

### What I hit

The OCR review gate looked like it "forgot" findings on push-backs and never auto-resolved
threads after fixes landed — agents kept resolving threads by hand. Controlled experiment
(zaio-week4-node-js-api#11, since closed): pushed a PR with 8 real findings, then a fix
commit mixing line-deletion fixes and in-place rewrites, and read every run log.

Findings: checkpoint memory on push-backs WORKS (later runs review only the new range);
the action's resolve_outdated auto-resolves threads only when the commented lines LEAVE the
diff. A fix that rewrites the commented lines in place — the most common kind — never
becomes outdated, so the thread stays open forever. Threads whose lines were deleted but
which a newer finding still covers are skipped too (overlap rule).

### What we decided

The reusable review workflow (Stelele/ocr-review) gains a post-review "verdict sweeper"
step: for each unresolved OCR-owned thread (no human replies), the review LLM judges the
finding against the current head version of the file and resolves the thread on a confident
"fixed". Fail-closed everywhere else.

### Why

Semantic fixes are invisible to GitHub's isOutdated flag; only an LLM verdict can see them.
Ownership rules mirror the action's own: bot author + ocr marker, no human replies. One
cheap LLM call per lingering thread, capped at 25/run — it meters the Go allowance, not
Actions minutes.

### The cost

- An LLM can wrongly judge a finding "fixed". Mitigated by high-confidence-only resolution
  and the existing merge gate (adjudication of findings before merge still applies).
- The sweeper resolves only OCR's own threads: a human who agrees with a lingering thread
  must still resolve or reply to it themselves — human engagement always wins.
- +1 LLM round-trip per lingering thread per run; a PR left unattended with 25 stale
  threads pays 25 calls per push.

## Jev screen default flipped to ON (per-repo opt-out) — opt-in made the default the expensive path

### What I hit

The Jev noul screen for the OCR verdict sweeper shipped as per-repo opt-in
(VERDICT_JEV_SCREEN=true). That made the DEFAULT path for all 110 repos the expensive
one: every lingering thread paid a ~15-20s glm-5.3-flash call that the calibrated screen
would have decided for free in a batched sub-second request.

### What we decided

The screen is ON by default; a repo opts out with VERDICT_JEV_SCREEN=false (0/no/off
accepted). All safeguards unchanged: no token, a non-opencode stage-2 provider without an
explicit JEV_TOKEN secret, fork PRs, and a moved head auto-disable the screen and fall
back to the reasoning LLM.

### Why

The opt-in was justified while the thresholds were unproven. After the calibration
(15 labeled threads: 0/9 false resolves; 3 "misses" were contestable labels) and the
594-thread backlog replay (0.8 min, $0, 0 failures, 2/2 mechanical spot-checks against
the resolve record), plus the security hardening rounds, the caution was spent and the
default was simply the worse configuration.

### The cost

- Default-on means the free tier now serves the whole account: sustained per-PR volume
  is untested beyond the 525k-token replay; if the free tier throttles, the screen
  fails closed to the reasoning LLM (cost, not breakage), and a paid jev-1.13 needs
  Console credits.
- Auto-resolution of low/medium findings now happens account-wide on merge rather than
  repo-by-repo decision; wrong auto-resolves are reversible (unresolve) but happen
  without a per-repo human first-run.

## Repository baseline restated: squash merges allowed, protection unchanged (withdraws the stale 0049/0054 squash lines)

### What I hit

Ratifying ADR 0055 (squash merges enabled account-wide) exposed that two LIVE core
sections still prescribe the old posture: ADR 0049's "Default branch is protected;
PR-only, no force push" and ADR 0054's "Repository baseline" both carry
`allow_squash_merge : false` in their PATCH blocks. Flagged in the
20261114-0650 question post; the owner authorized the core update this session.

### What we decided

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

### Why

The merge-methods line lived in two baseline sections and went stale the moment ADR 0055
landed — an agent obeying either PATCH block literally would re-disable squash
account-wide, silently undoing the owner's decision. Restating the baseline as a single
current section (and superseding the two stale ones citing this ADR) keeps every core
invariant: text-to-ADR correspondence, INDEX routing, no hand edits.

### The cost

- The archived sections' historical PATCH blocks (with squash=false) are out of INDEX
  routing — recovering any nuance they carried means reading `archive/workflow.md`.
- Agents citing "ADR 0049/0054" from memory still reference the old numbers; the ADR
  files remain as history but the live text is here.
- Merge-method changes now edit this section via the same supersede-and-restatement
  cycle rather than two places.
