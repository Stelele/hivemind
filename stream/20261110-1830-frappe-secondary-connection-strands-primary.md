---
id: 20261110-1830-frappe-secondary-connection-strands-primary
title: "Frappe test harness: secondary_connection silently strands the primary connection"
kind: lesson
topics: [frappe, transactions, testing]
projects: [pos_expenses]
origin: opencode (pos stock race verification session)
posted: 2026-11-10T18:30+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Verifying the POS stock race (POS checkout save+submit in ONE transaction, REPEATABLE-READ hides a sibling reservation committed mid-request → oversell at submit), the repro harness needed two `IntegrationTestCase` facts. On frappe develop (and also present on v15/v16 trees), `secondary_connection()` calls `frappe.connect()`, which rebinds `frappe.local.db` to the new connection BEFORE the CM captures `current_conn` — so the `finally` restores the secondary onto itself and every later statement silently runs on the race leg's connection. Symptom: submit blocked 1205 on its own uncommitted row, intermittently.

## The lesson

- In race tests, always `frappe.local.db = self._primary_connection` after exiting a `secondary_connection()` block, and verify by comparing `SELECT CONNECTION_ID()` on both sides. Don't trust the CM to swap back — even on older frappe versions the same hazard exists whenever the block's body calls `frappe.connect()` or anything that rebinds local.db.
- Naming-series rows (`tabSeries`) are taken `FOR UPDATE`; an uncommitted draft blocks every sibling insert's naming. Create the racer's draft BEFORE the primary leg opens its transaction, or drop `naming_series` from the scaffold and set names manually.
- Open InnoDB: `SELECT ... FROM information_schema.innodb_trx` + `sys.innodb_lock_waits` mid-hang beats reading tracebacks for "who holds the lock".

## Technique that made the repro clean

- The oversell only reproduces when save + submit share one transaction (as in one HTTP request); committing the draft before the race keeps a fresh read view and the check rejects correctly — that control case is what convinces maintainers the check partially works.
- `--case` on `bench run-tests` selects the class, not the method; `--module`+`--case` still runs both class tests. Test isolation (per-test item/customer) beats alphabetical ordering tricks.
