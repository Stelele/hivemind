# 0013. Maximum performance is the end result when asked for it

**Status:** accepted
**Date:** 2026-10-06
**Affects:** erpnext-dashboard, cms-system

## Context
2026-04-15 — "no I want maximum performance as the end result." Latency complaints follow: 2026-06-10 — "no thats too slow that fetch all runs every 5min who'se gonna wait for that."

## Decision
When performance is the stated goal, do not trade it away for tidiness without saying so. Pick the fast option and record the trade-off.

## Consequences
Acceptable latency. The cost is giving up readability and accepting more complex code.
