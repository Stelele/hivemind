---
id: 20261011-0739-theme-space-y-stacks-with-local-gap-instead-of-m
title: Theme space-y stacks with local gap instead of merging
kind: lesson
topics: [tailwind, css, layout]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-11T07:39+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
Phone cards rendered 64px apart with only 8px of margin on them. Misdiagnosed twice (card padding, forced min-heights) before measuring: the theme's page body carries `space-y-12` and the views added `flex flex-col gap-4` beside it.

## What we decided
Declare exactly one rhythm per list parent and neutralise the other (`flex flex-col gap-2 space-y-0`); cards carry no margins of their own.

## Why
`space-y` and `gap` are different properties, so they add instead of merging: 48 plus 16, invisibly, on every screen. Nothing in the toolchain flags it — it is valid CSS doing exactly what it says.

## The cost
A future theme change to the page rhythm reopens this silently; any screen that stops declaring `space-y-0` regains 48px gaps with no error anywhere.
