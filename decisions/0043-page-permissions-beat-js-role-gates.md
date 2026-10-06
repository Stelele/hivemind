# 0043. Page permissions beat JS role gates
**Status:** accepted
**Date:** 2026-10-06
**Affects:** awesome_restaurant3, erpnext-dashboard

## Context

A page rendered for the user while its JavaScript refused to act, producing a confusing
half-working UI.

Rendering happens before any of your JS runs, so permission resolution cannot be undone
by a client-side check.

## Decision

Page-level DocType permissions and JavaScript role gates can diverge. **The page `perm`
wins at render time.** A user can see a page that JS then blocks, or fail to see a page
whose JS would have allowed it.

## Consequences

Two systems to keep in sync, and the client-side one is advisory only. Treat JS role
checks as UX, never as authorization.
