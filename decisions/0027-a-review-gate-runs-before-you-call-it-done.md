# 0027. A review gate runs before you call it done

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
2026-06-04 → 2026-06-07 erpnext-dashboard: each task got both a 'review for spec compliance' and a 'review for code quality' agent. 2026-07-29 — "fire indipendant review agents with different models" · 2026-08-05 — "fire two adeversarial agents to criticise the spec".

## Decision
Spec compliance and code quality are reviewed by separate agents before completion. Adversarial spec critique happens before the build, not after.

## Consequences
Two decorrelated error sources catch what one lens cannot. The cost is real time and tokens per task.
