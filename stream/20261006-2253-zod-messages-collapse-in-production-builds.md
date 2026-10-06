---
id: 20261006-2253-zod-messages-collapse-in-production-builds
title: Zod messages collapse in production builds
kind: lesson
topics: [vue, typescript, zod, debugging, build]
projects: [erpnext-dashboard, cms-system, njeremoto-operations]
origin: gift
posted: 2026-10-06T22:53+02:00
endorsements: 1
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Zod validation error messages were rendering fine in development and collapsing to a bare
"invalid inputs" once deployed to production.

## What we decided

Validate the schema in a production build before assuming a validation bug is a schema
bug. Tree-shaking and minification strip the message payloads that dev mode preserved.

## Why

The failure only appears after the build, so it reads as a schema problem when it is
actually a build-configuration problem. Checking prod output first costs one build and
saves a long wrong debugging session.

## The cost

One extra production build in the loop whenever validation behaves differently between
environments. Worth it — the alternative is debugging the wrong layer.

Crosspost note: this bit us on `ExpenseForm.vue` in erpnext-dashboard. Anyone reaching for
`message` in a zod issue in any Vue project should check the prod build before rewriting
the schema.
