# 0038. Pinia stores use composition syntax and check error
**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, personal-site, njeremoto-operations

## Context

Store conventions existed in two repos with different registration styles.

Function-syntax stores read the same as the components that consume them, and the
`{ data, error }` shape from openapi-fetch forces the error branch to be visible.

## Decision

Pinia stores use the composition (function) syntax, one responsibility each, exposed
through a `use…Store` function.

```typescript
export const useBlogStore = defineStore('blogStore', () => {
  const blogs = ref<BlogResponse[]>([])

  async function update() {
    const client = await BackendApiSingleton.getInstance()
    const { data, error } = await client.GET('/blogs')
    if (error) return
    blogs.value = data ?? []
  }

  return { blogs, update }
})
```

- `ref()` not `reactive()` inside stores — consistent unwrapping.
- Handles the error case; never destructure `data` without checking `error`.

## Consequences

A little ceremony per store, and option-style stores will not match.
