# 0020. Pick the database by job, not by habit

**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, pesepay-payment-gateway, erpnext-dashboard, erpnext-cashbook-reconciliation

## Context
2026-04-21 — "I just want the @cms-system/backend/Api/ service to now use sqlite." · 2026-05-24 — "so for my database I'll go with postgres instead of sqlite. I want you to use the built in queue system that postgres offers."

## Decision
Not one database everywhere. Choose for the capability actually relied on and name it in the decision.

## Consequences
Each store earns its place. The cost is a mixed estate and two dialects of SQL to maintain.
