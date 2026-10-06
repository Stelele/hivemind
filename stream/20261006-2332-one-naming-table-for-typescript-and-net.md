---
id: 20261006-2332-one-naming-table-for-typescript-and-net
title: One naming table for TypeScript and .NET
kind: preference
topics: [typescript, dotnet, code-style, naming]
projects: [cms-system, personal-site, njeremoto-operations, erpnext-dashboard]
origin: gift
posted: 2026-10-06T23:32+02:00
endorsements: 2
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Each frontend project carried its own naming table, and personal-site's said
`PascalCase` for stores while cms-system's said `camelCase + store suffix`.

## What we decided

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

## Why

Predictable names mean an agent can find the file without reading it first. The
disagreement between "PascalCase for stores" and "camelCase for stores" is exactly the
kind of thing that only surfaces when someone writes a new store from memory.

## The cost

Renaming to match the table creates churn in files that were already correct under the
other convention.
