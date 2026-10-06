# 0035. Vue components: script setup, block order, withDefaults
**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, personal-site, njeremoto-operations, erpnext-dashboard

## Context

Three AGENTS.md files each carried their own Vue component structure, and they had
already diverged.

Ordering and `<script setup>` are enforced by ESLint in these repos anyway, so stating
them once on the board removes four places to keep in sync and gives non-Vue projects
the same shape.

## Decision

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

## Consequences

Enforced-by-linter rules are now documented twice. Accepted — the linter is the
enforcement, the board is the explanation.
