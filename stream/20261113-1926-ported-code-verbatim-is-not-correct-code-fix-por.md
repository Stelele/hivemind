---
id: 20261113-1926-ported-code-verbatim-is-not-correct-code-fix-por
title: Ported code verbatim is not correct code — fix ported defects against the target model
kind: decision
topics: [code-review, frappe, refunds]
projects: [erpnext-dashboard, awesome-dashboard]
origin: gift
posted: 2026-11-13T19:26+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit      While porting the refund feature from pos_expenses to awesome_dashboard, OCR flagged that the partial-refund payment proration (scaled off grand_total) fails ERPNext validation on change-given invoices. I deferred it as "inherited verbatim from production"; the owner overruled: fix it to match the ERPNext model — production features can have bugs.
## What we decided When porting logic between apps, "verbatim" preserves shape, not correctness. On discovering a ported defect, fix it against the target platform's own model (here: ERPNext's make_return_doc + POSInvoice.validate_payment_amount), with a bench e2e proving the failure mode before/after — don't defer to production precedent.
## Why             The port's whole purpose was to improve the feature; carrying a known money-math bug across the move defeats that. ERPNext's validation source and the bench make the fix cheap to prove.
## The cost        A move-PR now contains behavior changes beyond the move — reviewers must separate "moved code" from "fixed code" (mitigated: fix commits separated, each with its own e2e evidence).
