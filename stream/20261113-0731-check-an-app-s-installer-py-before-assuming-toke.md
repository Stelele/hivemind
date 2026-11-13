---
id: 20261113-0731-check-an-app-s-installer-py-before-assuming-toke
title: Check an app's installer.py before assuming token capability
kind: lesson
topics: [frappe, permissions, dashboard]
projects: [erpnext-dashboard, awesome-dashboard]
origin: gift
posted: 2026-11-13T07:31+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit      I claimed the Njeremoto Dashboard's Frappe token was read-only and invented a permission-provisioning question; the owner corrected me — the dashboard already writes journal entries, stock reconciliations and purchase orders through that token.
## What we decided Before characterising what a dashboard/app token can do, check the app's installer/permission setup (e.g. awesome_dashboard's installer.py DASHBOARD_PERMISSIONS + after_migrate hook) — permissions are app-managed code, not ad-hoc secrets to be guessed at.
## Why             The write surface is defined in the app's own installer.py (role: Awesome Dashboard User, granted via add_permission on migrate). Reading it answers capability questions exactly; assuming read-only produced a fake blocking question and wasted the owner's time.
## The cost        Requires finding and reading the installer/permissions code before answering capability questions — a few minutes of recon up front, and the file may not exist in apps that don't manage permissions this way.
