---
id: 20261112-2348-gateway-integrations-handle-every-terminal-not-p
title: Gateway integrations: handle every terminal-not-paid status, not just FAILED
kind: lesson
topics: [payments, pesepay, pos, api-integration, ux]
projects: [pesepay, frappe]
origin: opencode agent (pesepay cancelled-payment retry fix)
posted: 2026-11-12T23:48+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
POS retry UX died on customer-cancelled gateway payments: Pesepay reports CANCELLED (code 309) and 11 other terminal-not-paid statuses, but the integration only handled SUCCESS and FAILED. Everything else was treated as "still pending", so the cashier polled a dead transaction forever, got no terminal message, and every retry resumed the corpse while the submit guard (correctly) blocked the order.

Rules:
1. When integrating a payment gateway, mirror the provider's ENTIRE status table (in-progress / terminal-paid / terminal-not-paid) into a single shared constant, and use it in every consumer: client poll loop, scheduler sweeper, and result-callback webhook. Only the paid status fulfils; every terminal-not-paid status must release the pending request so the retry starts a fresh payment instead of resuming one that will never complete.
2. A submit guard (invoice must be backed by a completed gateway transaction) is what catches the leaked "paid without money" case — build that guard first, then make the retry UX recover from every terminal state.
3. Verify provider status semantics against their live docs, not memory: PARTIALLY_PAID was non-terminal ("don't stop polling"), CLOSED and CLOSED_PERIOD_ELAPSED share a status code (match on the status string, not the code).
