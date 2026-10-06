# 0037. One naming table for TypeScript and .NET
**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, personal-site, njeremoto-operations, erpnext-dashboard

## Context

Each frontend project carried its own naming table, and personal-site's said
`PascalCase` for stores while cms-system's said `camelCase + store suffix`.

Predictable names mean an agent can find the file without reading it first. The
disagreement between "PascalCase for stores" and "camelCase for stores" is exactly the
kind of thing that only surfaces when someone writes a new store from memory.

## Decision

| Thing | Convention | Example |
|---|---|---|
| Components | PascalCase | `NewBlogForm.vue` |
| Stores | camelCase file + `use…Store` | `blog-store.ts`, `useBlogStore` |
| Types | PascalCase | `BlogResponse`, `CreateBlogCommand` |
| Variables / functions | camelCase | `accessToken`, `blogList` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| CSS classes | Tailwind utilities, not custom names | `class="w-full h-full grid"` |

`.NET` side: namespaces and classes PascalCase, records for DTOs and commands/queries,
filename matches the type, method parameters camelCase.

## Consequences

Renaming to match the table creates churn in files that were already correct under the
other convention.
