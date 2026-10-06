# 0016. Compute presentation concerns on the client

**Status:** accepted
**Date:** 2026-10-06
**Affects:** erpnext-dashboard, cms-system

## Context
2026-04-15 — "do the date range calculations start, end, grouping etc in the frontend then pass the actual date arrays to the backend function."

## Decision
Date-range arithmetic and grouping that exist only to render a view belong in the frontend. Send the backend real ranges, not display buckets.

## Consequences
Fewer backend code paths and a smaller API. The cost is browser-side CPU on large datasets, and duplicated range semantics if another consumer needs buckets.
