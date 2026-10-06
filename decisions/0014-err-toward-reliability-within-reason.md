# 0014. Err toward reliability, within reason

**Status:** accepted
**Date:** 2026-10-06
**Affects:** pesepay-payment-gateway

## Context
2026-05-24 — "I'd err more towards reliability within reason so lets go with C."

## Decision
Default to the more reliable option when close, but never at unbounded complexity.

## Consequences
Fewer avoidable failures. The cost is that the 'within reason' ceiling is a judgment call and can be argued either way.
