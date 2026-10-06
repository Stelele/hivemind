# 0008. Flat response DTOs — no inheritance, no cycles

**Status:** accepted
**Date:** 2026-10-06
**Affects:** erpnext-dashboard backend, cms-system backend

## Context
2026-06-07 — "there's a lot of unnecessary inheritance and creating many extended DTOs for responses that really have no right to be there… I made a dumb decision of directly putting the command as the api request object instead of a proper request object leading to weird duplication." · 2026-06-08 — "there's an element of clyclical duplication like CompanyResponse -> site -> companyId. this doesn't make sense in the context of the response."

## Decision
Response DTOs are flat and shaped for the response. No inheritance chains, no back-references. Request objects are distinct from commands.

## Consequences
Serialisation is obvious and no cycles break JSON. The cost is duplication when two responses genuinely share fields, and the discipline to keep request and command types separate.
