# 0028. Show the instructions and the reasoning

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project, every agent

## Context
2026-05-23 — "I don't care about your edit, I care about the instructions either you or your subagents ran when they were coming to the conclusions you made, what did they do."

## Decision
When reporting a conclusion, especially one reached via a subagent, state what you instructed and what came back. The reasoning is the deliverable.

## Consequences
Conclusions can be audited and corrected. The cost is longer replies than the bare diff.
