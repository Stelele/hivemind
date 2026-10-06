# 0007. No non-null assertions — widen the type

**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system frontend, any TS project

## Context
2026-05-17 — "there's too much abuse of ! for enforcing a type is not null, the type files have been updated to be more specific so this isn't necessary anymore, can you clean it all up."

## Decision
Do not use `!` to silence a nullable type. Widen the type at its source.

## Consequences
Types carry real information and asserts disappear. The cost is more type refinement work up front, and a wider type can be less honest about what is actually guaranteed.
