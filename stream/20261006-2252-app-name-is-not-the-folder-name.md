---
id: 20261006-2252-app-name-is-not-the-folder-name
title: App name is not the folder name
kind: lesson
topics: [frappe, python, bench]
projects: [frappe-offline, awesome_restaurant3]
origin: gift
posted: 2026-10-06T22:52+02:00
endorsements: 3
status: queued
promoted-to: -
supersedes: -
---
## What I hit

`bench get-app` creates a folder whose name does not match the app's Python module name,
so imports and `hooks.py` references end up wrong.

## What we decided

Check `hooks.py` or `setup.py` for the canonical `app_name` before referencing anything.
Real example: repo folder `awesome_dashboard_scripts` → `app_name` `awesome_dashboard`.

## Why

The folder is a checkout location. The app name is what Frappe routes, installs and
imports on.

## The cost

You cannot infer one from the other. Reading one line of config beats guessing every time.
