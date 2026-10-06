# 0033. App name is not the folder name
**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-offline, awesome_restaurant3

## Context

`bench get-app` creates a folder whose name does not match the app's Python module name,
so imports and `hooks.py` references end up wrong.

The folder is a checkout location. The app name is what Frappe routes, installs and
imports on.

## Decision

Check `hooks.py` or `setup.py` for the canonical `app_name` before referencing anything.
Real example: repo folder `awesome_dashboard_scripts` → `app_name` `awesome_dashboard`.

## Consequences

You cannot infer one from the other. Reading one line of config beats guessing every time.
