# 0003. Keep CI under ten minutes

**Status:** accepted
**Date:** 2026-10-06
**Affects:** repos with .github/workflows

## Context
2026-09-08 — "I want the entire ci pipeline to run in under 10 mins. currently too much developer time is wasted waiting for the pipeline to finish."

## Decision
A change that pushes the pipeline past ~10 minutes is treated as a regression to fix in the same change.

## Consequences
Constrains how much gets bolted onto CI. The cost is forgoing slow-but-thorough jobs that would have caught more.
