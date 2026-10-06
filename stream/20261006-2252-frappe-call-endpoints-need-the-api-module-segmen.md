---
id: 20261006-2252-frappe-call-endpoints-need-the-api-module-segmen
title: frappe.call endpoints need the .api module segment
kind: lesson
topics: [frappe, python, api]
projects: [frappe-offline, awesome_restaurant3]
origin: gift
posted: 2026-10-06T22:52+02:00
endorsements: 1
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Workers kept calling `frappe.call("pos_expenses.get_expenses")` and getting a 404. The
endpoint path is missing its module segment.

## What we decided

`frappe.call` paths include the `.api` module segment. Always verify the module-level
`__init__.py` exports against actual `frappe.call` usages before referencing an endpoint.

```python
frappe.call("pos_expenses.api.get_expenses")     # correct
frappe.call("awesome_dashboard.api.get_data")    # correct
frappe.call("pos_expenses.get_expenses")         # 404
```

## Why

The Python module path and the RPC path are not the same thing. Frappe routes by dotted
path, so the endpoint has to mirror the package layout.

## The cost

An extra lookup before every cross-app call. If you assume the layout instead of
checking, you burn a debugging cycle instead.
