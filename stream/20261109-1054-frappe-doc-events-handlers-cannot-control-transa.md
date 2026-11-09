---
id: 20261109-1054-frappe-doc-events-handlers-cannot-control-transa
title: Frappe: doc_events handlers cannot control transactions — use extend_doctype_class
kind: lesson
topics: [frappe, transactions, doc-events, extend-doctype-class]
projects: [pos_expenses]
origin: opencode (pos_expenses race guard PR review)
posted: 2026-11-09T10:54+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
# Frappe: doc_events handlers cannot control transactions — use extend_doctype_class

## What I hit

Building the POS stock race guard (pos_expenses PR #6, Nov 2026), the guard needed to
restart the request's read view mid-submit (`frappe.db.commit(chain=True)`) to see a
sibling reservation that committed after the invoice validated. Wired as a
`doc_events` handler, every commit/rollback is **silently ignored** — Frappe's
`Document.hook` compose runner wraps ALL doc_events handlers with
`frappe.db._disable_transaction_control += 1` (frappe/model/document.py ~1885), and
`Database.commit` early-returns with only a UserWarning when set.

The working seam is `extend_doctype_class` in hooks.py: a mixin class placed BEFORE
the controller in the MRO. Its own `before_submit` (same name) runs via
`Document.run_method` → the class method executes OUTSIDE the txn-control wrapper,
so it may commit/rollback. Method replacement via `override_doctype_class` works the
same but caps you at one override app and trips the frappe `override-doctype-class`
semgrep rule.

## The cost

- Progress: the guard's read-view restart works under commit-and-chains (and the
  resulting REPEATABLE-READ staleness — the entire reason the POS reservation
  race exists — is solvable with `SELECT ... FOR UPDATE` bin anchors + fresh
  snapshots).
- Price: the mixin runs as part of the submit's own class. Errors treated as hook
  noise elsewhere still roll back everything in the transaction, and any other
  app's mixin earlier in the MRO that writes during its own before_submit gets
  committed by our chain — documented, accepted, noted in review.

Related:
- `frappe.tests.classes.integration_test_case.IntegrationTestCase` ships
  `secondary_connection()` and `primary_connection()` context managers — a second
  DB connection in-process, exactly the primitive you want for testing concurrent
  cashiers without threads.
- `frappe.db.commit(chain=True)` → SQL `COMMIT AND CHAIN`: releases the locks,
  starts a fresh read view, keeps a transaction open. No savepoint can do that.
