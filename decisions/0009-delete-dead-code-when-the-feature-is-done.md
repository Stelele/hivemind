# 0009. Delete dead code when the feature is done

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
2026-04-16 — "now I want to remove the unused code since we're now done."

## Decision
When a feature lands, remove the code it replaced.

## Consequences
No zombie branches in the codebase. The cost is losing the fallback of keeping old code around, which is almost never worth it.
