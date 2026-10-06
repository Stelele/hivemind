# 0018. Explicit save over autosave

**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-bench

## Context
2026-07-20 — "this is becoming an annoying feature and becoming overly complicated. lets remove the autosaving feature completly. instead, lets have a dedicated save button in the same line."

## Decision
Prefer one explicit save action over autosave when autosave fights the user.

## Consequences
Predictable saves. The cost is one extra interaction per save, and lost work if the user forgets.
