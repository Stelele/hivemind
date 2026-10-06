# 0002. Batch the change, then test once

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
2026-05-27 — "don't run tests on every change, its too slow, do all your changes in one go then test afterwards."

## Decision
Make the full set of edits, then run the suite once at the end.

## Consequences
Far less wall-clock per task. The cost: a failure found late may span several edits, so error messages need more context to localise.
