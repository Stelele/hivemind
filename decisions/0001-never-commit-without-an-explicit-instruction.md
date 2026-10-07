# 0001. Never commit without an explicit instruction

**Status:** superseded by 0049
**Superseded:** 2026-10-07
**Date:** 2026-10-06
**Affects:** every project, every agent

## Context
2026-06-05 — "I don't like it when you automatically commit code either by you or your subagents when you do changes. I like to see everything thats written and give reviews." Repeated unprompted across cms-system (2026-05-12, 05-17), personal-site (2026-05-18, 05-22) and erpnext-dashboard.

## Decision
Superseded. Agents never commit, push, or open a PR. The change stays in the working tree. The no-commit instruction is passed down to every dispatched subagent.

## Consequences
Work accumulates as reviewable diffs instead of disappearing into history. The cost is that clean checkpoints must be made explicitly, and agent runs end dirty.
