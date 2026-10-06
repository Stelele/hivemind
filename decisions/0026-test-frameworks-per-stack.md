# 0026. Test frameworks per stack

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
`cms-system/frontend/AGENTS.md` and `personal-site/frontend/AGENTS.md` both record "No test framework is currently installed" alongside "when adding tests use Vitest / Playwright" · xUnit in PesePay · Cypress + pytest in awesome_restaurant3.

## Decision
Vitest + Playwright for Vue/TS, xUnit for .NET, Cypress + pytest for Frappe apps.

## Consequences
Consistent choices. The cost is most projects still have no suite, so the browser rule above carries the verification burden.
