# 0032. Multi-agent review is the default

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
The reviewer-prompt pattern of 2026-06-04 → 2026-06-07, plus the `swarm` and `team` skills in `~/.config/opencode/skills/` and the swarm-execution rule mapping subagent roles.

## Decision
For substantial work, dispatch review agents on distinct lenses and prefer different models so errors decorrelate. Cheap workers implement, reviewers judge.

## Consequences
Errors decorrelate across models. The cost is orchestration overhead and more tokens per task.
