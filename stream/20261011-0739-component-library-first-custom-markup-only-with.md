---
id: 20261011-0739-component-library-first-custom-markup-only-with
title: Component library first, custom markup only with a stated reason
kind: preference
topics: [nuxt-ui, code-style]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-11T07:39+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
Corrected twice in one session for hand-rolling markup and styles the component library already provides (tab bar, cards) instead of using it.

## What we decided
Reach for the project's component library first; hand-rolled markup needs a reason stated out loud.

## Why
Library components carry theme behavior (both color modes), accessibility semantics, and active states that custom markup silently drops — the tab bar lost all three at once. The custom version also passed every automated check, so nothing but review catches the downgrade.

## The cost
Occasionally the library genuinely lacks the pattern (the journal table predates the card language for a reason); those cases get their reason recorded instead of a silent custom build.
