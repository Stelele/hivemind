# 0005. Chain setup scripts, and end with a verifier

**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-offline, frappe-bench

## Context
2026-07-23 — "I'd prefer these scripts to be chained. its kinda a pain that I would need to run them manually. I'd also like a final script that verifys everything is set up correctly."

## Decision
Multi-step environment setup ships as an ordered chain plus a final verification script.

## Consequences
Setup is one command and self-checking. The cost is the verifier must be maintained as the environment changes.
