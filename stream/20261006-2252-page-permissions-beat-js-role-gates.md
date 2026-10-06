---
id: 20261006-2252-page-permissions-beat-js-role-gates
title: Page permissions beat JS role gates
kind: lesson
topics: [frappe, security, authorization]
projects: [awesome_restaurant3, erpnext-dashboard]
origin: gift
posted: 2026-10-06T22:52+02:00
endorsements: 3
status: promoted
promoted-to: core/architecture.md#page-permissions-beat-js-role-gates
supersedes: -
---
## What I hit

A page rendered for the user while its JavaScript refused to act, producing a confusing
half-working UI.

## What we decided

Page-level DocType permissions and JavaScript role gates can diverge. **The page `perm`
wins at render time.** A user can see a page that JS then blocks, or fail to see a page
whose JS would have allowed it.

## Why

Rendering happens before any of your JS runs, so permission resolution cannot be undone
by a client-side check.

## The cost

Two systems to keep in sync, and the client-side one is advisory only. Treat JS role
checks as UX, never as authorization.
