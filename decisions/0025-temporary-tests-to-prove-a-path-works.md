# 0025. Temporary tests to prove a path works

**Status:** accepted
**Date:** 2026-10-06
**Affects:** projects without a test suite

## Context
2026-05-12 — "you can write temporary tests to verify both the backup and upload, get, delete file endpoints work and same for the database."

## Decision
Where no suite exists, write throwaway tests to prove the path works end to end, then agree with the user whether they stay.

## Consequences
Claims of 'it works' are backed by execution. The cost is throwaway tests calcifying if nobody deletes them.
