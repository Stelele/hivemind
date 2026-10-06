# 0019. Deployable work is Vue 3 + TypeScript and .NET 10

**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, erpnext-dashboard, njeremoto-operations, class-booking-system, personal-site

## Context
Consistent across 15+ sessions in the five repos above: Vue 3 + Vite + Pinia + Tailwind + @nuxt/ui front end, .NET 10 Minimal API + EF Core + CQRS/MediatR back end.

## Decision
Default application shape unless the project has already committed otherwise.

## Consequences
Every project starts from a known baseline and cross-project patterns transfer. The cost is being wrong for a job that needs something else entirely.
