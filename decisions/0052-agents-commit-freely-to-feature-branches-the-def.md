# 0052. Agents commit freely to feature branches; the default branch stays PR-only
**Status:** accepted
**Date:** 2026-10-16
**Affects:** hivemind, camera-nvr

## Context

ADR 0001 — "never commit without an explicit instruction" — was superseded by ADR 0049 on
2026-10-07. It is still quoted as a live rule in 18 places: `core/workflow.md`, the global
`~/.config/opencode/AGENTS.md`, `hivemind/AGENTS.md`, and 16 project `AGENTS.md` files, all
citing it by number.

Meanwhile the part of it that still bites is pure ceremony. With the default branch
platform-protected, an agent asking "may I commit?" before touching a throwaway feature
branch is asking permission for something that cannot reach `main` and cannot be undone
silently.

The rule that was supposed to protect work had become a prompt, not a control.

ADR 0049 already made this argument for the default branch: *a rule that lives only in an
instruction file is one careless session away from being broken.* The same argument applies
to the agent-side half, and it has now demonstrably decayed — 18 files still cite a
superseded ADR as though it were current. Extending the platform-enforced posture to
commits on feature branches keeps one gate instead of two, and drops the one that rotted.

Feature-branch pushes are also visible and cheap to undo. The irreversible step is the merge
into the default branch, and that is exactly where the control belongs.

## Decision

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

## Consequences

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
