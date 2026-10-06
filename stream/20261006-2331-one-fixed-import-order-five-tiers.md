---
id: 20261006-2331-one-fixed-import-order-five-tiers
title: One fixed import order, five tiers
kind: preference
topics: [typescript, vue, code-style, imports]
projects: [cms-system, personal-site, njeremoto-operations]
origin: gift
posted: 2026-10-06T23:31+02:00
endorsements: 2
status: stream
promoted-to: -
supersedes: -
---
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
