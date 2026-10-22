---
id: 20261022-2047-umodal-in-nuxt-ui-v4-binds-v-model-open-not-v-mo
title: UModal in Nuxt UI v4 binds v-model:open, not v-model
kind: lesson
topics: [vue, nuxt-ui]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-22T20:47+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

In a Vue 3 + `@nuxt/ui` v4 (Vite/unplugin, not Nuxt) app, a `UModal` bound with `v-model="open"` is silently inert — no error, no warning, tests pass. Only clicking it in the real app shows nothing happens. Nuxt UI v4 modals bind with `v-model:open`.

## What we decided

Bind overlay components (`UModal`, and check `UDrawer`/`UPopover`) with `v-model:open` in Vue apps on this stack, never bare `v-model`.

## Why

v4's component API renamed the model prop; `modelValue` isn't the trigger. The failure mode is silent, so it costs a live-debug cycle every time it's retyped.

## The cost

`v-model:open` is more to type and diverges from plain-Vue components where `v-model` is standard; older files handwritten with `v-model` need fixing when next touched.
