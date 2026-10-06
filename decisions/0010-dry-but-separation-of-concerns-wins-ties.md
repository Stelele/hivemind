# 0010. DRY, but separation of concerns wins ties

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
2026-04-16 — "minor refactoring so we honer the pragramtic engineers principle of DRY and appropropriate sepation of concerns." · 2026-05-22 — "thats also duplication, can you help me consolidate the logic between the two functions."

## Decision
Remove real duplication; do not merge separately-meaningful things merely because their bodies resemble each other.

## Consequences
Less accidental coupling without collapsing distinct responsibilities. The cost is some near-duplicate code surviving deliberately.
