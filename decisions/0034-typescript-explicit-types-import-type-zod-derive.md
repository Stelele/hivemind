# 0034. TypeScript: explicit types, import type, zod-derived types
**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, personal-site, njeremoto-operations

## Context

The same TypeScript conventions were restated in three places at once —
`cms-system/AGENTS.md`, `cms-system/frontend/AGENTS.md` and
`personal-site/frontend/AGENTS.md` — and kept drifting apart.

When the same rule lives in three files, it gets updated in two of them. The drift is
silent and the wrong file becomes the reference.

## Decision

```typescript
// explicit types on params and return values
const fetchBlogs = async (): Promise<BlogResponse[]> => {
  const { data } = await client.GET('/blogs')
  return data ?? []          // always handle the null case
}

// type-only imports use `import type`
import type { components } from '@/services/backend/schema'

// runtime validation with zod, types derived from the schema
const schema = z.object({ name: z.string().min(4) })
type Schema = z.output<typeof schema>
```

- `strict: true` stays on. Never disable a strict check to make a type fit.
- Explicit return types unless inference is unambiguous.
- `interface` for object shapes, `type` for unions and aliases.
- Derive types from the runtime validator so they cannot drift.

## Consequences

Explicit return types are noise where inference is obvious, and `z.output` costs a
line. Bought: types that cannot contradict the validator.
