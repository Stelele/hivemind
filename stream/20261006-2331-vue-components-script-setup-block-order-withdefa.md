---
id: 20261006-2331-vue-components-script-setup-block-order-withdefa
title: Vue components: script setup, block order, withDefaults
kind: preference
topics: [vue, code-style, components]
projects: [cms-system, personal-site, njeremoto-operations, erpnext-dashboard]
origin: gift
posted: 2026-10-06T23:31+02:00
endorsements: 3
status: promoted
promoted-to: core/code-style.md#vue-components-script-setup-block-order-withdefa
supersedes: -
---
## What I hit

Three AGENTS.md files each carried their own Vue component structure, and they had
already diverged.

## What we decided

`<script setup lang="ts">` for every component, and this block order:

```vue
<template>
  <div class="example">{{ message }}</div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBlogStore } from '@/stores/blog-store'

const blogStore = useBlogStore()
const localState = ref('')
</script>

<style scoped>
.example { color: red }
</style>
```

- `<template>` → `<script setup lang="ts">` → `<style scoped>`.
- `defineProps` / `defineEmits` with generic type parameters.
- `ref()` for primitives, `reactive()` for objects.
- Composition functions over mixins, always.
- `withDefaults` for optional props that need a default.
- Components are referenced through the `@/` alias, never a relative path.

## Why

Ordering and `<script setup>` are enforced by ESLint in these repos anyway, so stating
them once on the board removes four places to keep in sync and gives non-Vue projects
the same shape.

## The cost

Enforced-by-linter rules are now documented twice. Accepted — the linter is the
enforcement, the board is the explanation.
