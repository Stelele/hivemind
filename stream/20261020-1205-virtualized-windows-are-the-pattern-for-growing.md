---
id: 20261020-1205-virtualized-windows-are-the-pattern-for-growing
title: Virtualized windows are the pattern for growing lists in Vue apps
kind: preference
topics: [vue, ui, lists, frontend-pattern]
projects: [njeremoto-operations, erpnext-dashboard]
origin: njeremoto-operations session
posted: 2026-10-20T12:05+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Signal (stated by gift while reviewing PR for njeremoto-operations): for long/admin-bound lists in Vue frontends, the approved shape is the one erpnext-dashboard's sales page uses — a fixed-height, own-scroll container with `useVisibleWindow`: rAF-throttled scroll metrics, only the visible slice mounted, exact-height top/bottom spacers so the scrollbar is the whole document (desktop UTable `virtualize` where a table exists). A growing client-side slice with a "Show N more" control (or a page bar) is not accepted for these lists, even though it's lighter to build, because DOM grows with everything the user reads and the window has no scrollbar to speak of.

Uneven rows need one note when porting: uniform sales rows make rowHeight exact; card lists should register rows with a shared ResizeObserver and measure real heights after first paint, with rowHeight only the initial guess. Spacing between rows must be padding, not margin, or the measured box and the document disagree.

Outcomes:
- erpnext-dashboard sells the pattern; njeremoto-operations ADR 0065 documents its port (measured-heights variant).
- When a project needs reading lists, copy the working composable before inventing an IntersectionObserver-grow variant.
