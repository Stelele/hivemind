---
id: 20261011-0738-design-system-values-outside-the-public-surface
title: Design-system values outside the public surface lie
kind: lesson
topics: [nuxt-ui, css, dark-mode]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-11T07:38+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
Three styling defects that all passed typecheck and unit tests: a tab bar painted transparent from a raw `--ui-bg-default` variable that is never assigned; cards given `bg-elevated` that vanished because it resolves to exactly the page background in dark mode; and `UCard :as="RouterLink"` rendering bordered in the DOM and invisible on screen.

## What we decided
Style only through the design system's public surface — components, props, `ui` keys, utilities — and verify every visual change with screenshots in both color modes.

## Why
Raw theme variables and polymorphic roots (`:as`) bypass every check the toolchain has: the compiler accepts them, jsdom cannot see paint, and two of the three failed only in dark mode. The DOM inspector actively misleads here — bordered in markup, flat in pixels.

## The cost
Screenshots become part of verification for styling work, which is slower than unit tests and the only thing that catches this class.
