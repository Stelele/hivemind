# 0039. One typed API client, generated schema, null-safe
**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, personal-site, erpnext-dashboard

## Context

Both frontends fetch through a generated API layer, but each had documented its own
singleton in isolation.

Generated types mean the frontend breaks at compile time when the backend contract
changes, instead of at runtime in front of a user.

## Decision

The shape, not the class name:

- One client instance for the app, created lazily. Do not construct a new client per call.
- The client is typed from the **generated** OpenAPI schema, never hand-written types.
- Derive `zod` schemas for forms from the same schema module.
- `return data ?? fallback` — every response is treated as possibly null.

```typescript
const client = await BackendApiSingleton.getInstance()
const { data, error } = await client.GET('/blogs')
if (error) return
const blogs = data ?? []
```

## Consequences

The API surface is only as good as the spec — a wrong OpenAPI document produces
confidently wrong types.
