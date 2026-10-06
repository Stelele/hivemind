# 0040. Frappe.call endpoints need the .api module segment
**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-offline, awesome_restaurant3

## Context

Workers kept calling `frappe.call("pos_expenses.get_expenses")` and getting a 404. The
endpoint path is missing its module segment.

The Python module path and the RPC path are not the same thing. Frappe routes by dotted
path, so the endpoint has to mirror the package layout.

## Decision

`frappe.call` paths include the `.api` module segment. Always verify the module-level
`__init__.py` exports against actual `frappe.call` usages before referencing an endpoint.

```python
frappe.call("pos_expenses.api.get_expenses")     # correct
frappe.call("awesome_dashboard.api.get_data")    # correct
frappe.call("pos_expenses.get_expenses")         # 404
```

## Consequences

An extra lookup before every cross-app call. If you assume the layout instead of
checking, you burn a debugging cycle instead.
