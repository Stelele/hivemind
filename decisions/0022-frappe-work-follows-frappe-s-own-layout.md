# 0022. Frappe work follows Frappe's own layout

**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-offline, frappe-bench, awesome_restaurant3

## Context
`.field-guide/index.md` — frappe.call endpoint paths include the module segment; `bench switch-to-branch` not `switch-to-version`; `bench run-tests --app <app>`. 28+ sessions in frappe-offline and frappe-bench.

## Decision
hooks.py, a real Python package layout, whitelisted functions in an `api/` module, and Frappe's documented CLI verbs.

## Consequences
Frappe extensions behave like Frappe extensions. The cost is none real, but the conventions are invisible to anyone who has not read the framework.
