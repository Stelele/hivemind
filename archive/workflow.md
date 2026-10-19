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
