---
id: 20261114-1953-validate-copied-data-guards-must-skip-is-consoli
title: Validate-copied-data guards must skip is_consolidated merge copies
kind: lesson
topics: [frappe, python]
projects: [pos_expenses]
origin: gift
posted: 2026-11-14T19:53+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Guard hooks that validate business data must skip system-generated copies. Frappe's POS Closing merges submitted POS Invoices into a fresh Sales Invoice (`is_consolidated = 1`) with payment rows copied over; any `before_submit` guard that checks "does a payment/IR reference *this* document" can never pass for that copy, because the evidence references the source invoices. Same shape will bite refund/order guards, loyalty hooks, or any app-level validation attached to Sales Invoice: check `is_consolidated` (and `is_return`) before validating copied rows. erpnext's own hooks do this consistently (loyalty in sales_invoice.py) — treat `is_consolidated` as the standard skip marker. Cost: one extra early return and a test; without it the guard blocks every POS closing day that used the gateway, discovered live on bsmitech.

## The cost

One early return plus one regression test (~30 lines). The risk of the fix is a guard gap: a consolidated invoice can no longer be independently re-validated — accepted because the source POS Invoices were already guarded at their own submit, so there is no new cashier input to validate.
