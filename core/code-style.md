# Code style

## No non-null assertions — make the types specific instead

`!` used to silence a nullable type is a bug marker, not a fix. When you find them,
widen the type at the source instead of asserting at the point of use.

*Evidence: 2026-05-17 — "there's too much abuse of ! for enforcing a type is not null, the
type files have been updated to be more specific so this isn't necessary anymore, can you
clean it all up."*
→ [ADR 0007](../decisions/0007-no-non-null-assertions-widen-the-type.md)

## Flat response DTOs — no inheritance chains, no cycles

Response DTOs are flat structures built for the response. Do not build an inheritance
hierarchy of extended DTOs, and do not let a response reference an object that points
back (e.g. `CompanyResponse → site → companyId`). A request object is not the same thing
as a command — do not reuse it as one and call it a day.

*Evidence: 2026-06-07 — "there's a lot of unnecessary inheritance and creating many
extended DTOs for responses that really have no right to be there… I made a dumb decision
of directly putting the command as the api request object instead of a proper request
object leading to weird duplication." · 2026-06-08 — "there's an element of clyclical
duplication like CompanyResponse -> site -> companyId. this doesn't make sense in the
context of the response."*
→ [ADR 0008](../decisions/0008-flat-response-dtos-no-inheritance-no-cycles.md)

## Delete dead code when the feature is done

When a feature lands and code it replaced is now unreachable, remove the dead code. Do not
leave it "just in case", and do not leave unused exports, variables or whole files.

*Evidence: 2026-04-16 — "now I want to remove the unused code since we're now done."*
→ [ADR 0009](../decisions/0009-delete-dead-code-when-the-feature-is-done.md)

## DRY, but separation of concerns wins ties

Apply the pragmatic engineer's reading of DRY: remove genuine duplication, but do not merge
things that are separately meaningful just because their bodies look alike.

*Evidence: 2026-04-16 — "minor refactoring so we honer the pragramtic engineers principle of
DRY and appropropriate sepation of concerns." · 2026-05-22 — "thats also duplication, can you
help me consolidate the logic between the two functions."*
→ [ADR 0010](../decisions/0010-dry-but-separation-of-concerns-wins-ties.md)

## No over-assertion on optionality

Prefer returning absent/optional over inventing a sentinel value. `null`/`undefined` is an
acceptable answer; a magic default that silently becomes real data is not.

## typescript-explicit-types-import-type-zod-derive

## What I hit

The same TypeScript conventions were restated in three places at once —
`cms-system/AGENTS.md`, `cms-system/frontend/AGENTS.md` and
`personal-site/frontend/AGENTS.md` — and kept drifting apart.

## What we decided

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

## Why

When the same rule lives in three files, it gets updated in two of them. The drift is
silent and the wrong file becomes the reference.

## The cost

Explicit return types are noise where inference is obvious, and `z.output` costs a
line. Bought: types that cannot contradict the validator.

## vue-components-script-setup-block-order-withdefa

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

## one-fixed-import-order-five-tiers

## What I hit

Import ordering was specified two different ways in two files, one saying "internal
absolute" third and the other putting path aliases fourth.

## What we decided

One fixed order:

```
1. vue / pinia / stdlib        import { ref } from 'vue'
2. type-only imports           import type { Foo } from './foo'
3. external libraries          import { z } from 'zod'
4. path aliases                import X from '@/components/X.vue'
5. relative imports            import { y } from './utils'
```

## Why

A stable order makes diffs small and removes a recurring point of disagreement in review.
Two variants of the same rule is worse than no rule.

## The cost

A strict order means reorganising imports in older files when they are next touched,
which produces occasional noisy diffs.
