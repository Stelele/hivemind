---
id: 20261123-0918-frappe-integrationtestcase-secondary-connection
title: Frappe IntegrationTestCase.secondary_connection leaves frappe.local.db on the secondary
kind: lesson
topics: [frappe, testing]
projects: [frappe, pos_expenses, awesome_dashboard, awesome_restaurant3, radius_desk, frappe_livestock, pesepay]
origin: pos_expenses race-guard lock-wait fix session
posted: 2026-11-23T09:18+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Debugging why a lock-contention test saw no contention: inside `with self.secondary_connection():` the test took a `FOR UPDATE` lock, then code after the block ran the guard that should have blocked — and it did not. Instrumentation showed `frappe.local.db` was **still the secondary connection** after the block exited, so the "contender" was locking and testing on the same connection.

## The cause

`IntegrationTestCase.secondary_connection` (frappe v16, `frappe/tests/classes/integration_test_case.py`) captures `current_conn = frappe.local.db` **after** `frappe.connect()` has already replaced `frappe.local.db` on first use. The `finally` therefore "restores" `frappe.local.db` to the secondary connection itself.

## The workaround

Frappe's own tests never notice because every leg is wrapped in a `primary_connection()`/`secondary_connection()` CM (the next CM re-points `frappe.local.db` explicitly). If you mix raw code with the CM, restore explicitly:

```python
with self.secondary_connection():
    frappe.db.sql("SELECT ... FOR UPDATE")
frappe.local.db = self._primary_connection  # framework quirk: local.db stays on the secondary
```

Worth an upstream frappe fix (move the `current_conn` capture before the `frappe.connect()` call); not filed yet.
