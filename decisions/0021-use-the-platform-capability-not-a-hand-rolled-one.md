# 0021. Use the platform capability, not a hand-rolled one

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
2026-06-24 — "lets go with hosting on cloudflare R2, I've got a public bucket there already."

## Decision
Where a managed service or platform primitive exists, use it instead of writing the equivalent.

## Consequences
Less code to own. The cost is a vendor dependency and its pricing.
