# 0015. Keep changes narrowly scoped

**Status:** accepted
**Date:** 2026-10-06
**Affects:** erpnext-dashboard, every project

## Context
2026-06-13 — "there's no reason to do such a large sweep of all the files and the file name is not guaranteed."

## Decision
Do not sweep the codebase when the fix is local. A change that had to touch twenty files is usually solving a different problem.

## Consequences
Reviewable diffs and no incidental breakage. The cost: a genuine cross-cutting fix has to be argued for explicitly.
