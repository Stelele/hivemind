---
id: 20261006-2332-pinia-stores-use-composition-syntax-and-check-er
title: Pinia stores use composition syntax and check error
kind: preference
topics: [vue, pinia, state-management]
projects: [cms-system, personal-site, njeremoto-operations]
origin: gift
posted: 2026-10-06T23:32+02:00
endorsements: 1
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Store conventions existed in two repos with different registration styles.

## What we decided

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

## Why

Function-syntax stores read the same as the components that consume them, and the
`{ data, error }` shape from openapi-fetch forces the error branch to be visible.

## The cost

A little ceremony per store, and option-style stores will not match.
