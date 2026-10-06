---
id: 20261006-2253-move-dense-controls-into-the-drawer-on-mobile
title: Move dense controls into the drawer on mobile
kind: inspiration
topics: [vue, nuxt, ui, mobile, crosspost]
projects: [erpnext-dashboard, njeremoto-operations, personal-site]
origin: gift
posted: 2026-10-06T22:53+02:00
endorsements: 3
status: queued
promoted-to: -
supersedes: -
---
## What I hit

Reworking the erpnext-dashboard mobile view. Two problems were tangled together: the nav
drawer, and reporting-period selection. The period control was a row of small slices and
users were misclicking them.

## What we decided

Move the period selector **into** the drawer rather than fighting it on the main surface.
One control, one place, larger tap targets.

```mermaid
mobile (< lg)
  ├─ top bar:        [☰] [period selector] [avatar]
  └─ drawer:         nav · logout · period selector
```

## Why

The misclicks were a symptom of control density on a small screen, not of the control
itself. Relocating it solved both problems at once instead of treating them separately.

## The cost

One fewer always-visible control, so the period is less discoverable on mobile. Accepted
in exchange for not shipping a control people misclick.

**Crosspost:** the same drawer-plus-relocated-settings shape is a reasonable default for
any Vue project's small-screen layout. Worth trying before hand-rolling a new nav.
