# 0012. Simplicity outranks resilience when volume does not justify it

**Status:** accepted
**Date:** 2026-10-06
**Affects:** pesepay-payment-gateway, any small service

## Context
2026-06-02 — "the current service is heavily over engineered to thee point of being useless. All I really care about is the raw payment and the things like fault tolerance and such don't make sense considering the current transaction volume which is quite literally non existent."

## Decision
Justify fault tolerance, queues and retry machinery against actual volume. If volume does not exist, do not build them.

## Consequences
The service stays readable and debuggable. The cost is genuine exposure if volume grows without anyone revisiting the decision.
