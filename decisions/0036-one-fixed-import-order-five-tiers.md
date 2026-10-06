# 0036. One fixed import order, five tiers
**Status:** accepted
**Date:** 2026-10-06
**Affects:** cms-system, personal-site, njeremoto-operations

## Context

Import ordering was specified two different ways in two files, one saying "internal
absolute" third and the other putting path aliases fourth.

A stable order makes diffs small and removes a recurring point of disagreement in review.
Two variants of the same rule is worse than no rule.

## Decision

One fixed order:

```
1. vue / pinia / stdlib        import { ref } from 'vue'
2. type-only imports           import type { Foo } from './foo'
3. external libraries          import { z } from 'zod'
4. path aliases                import X from '@/components/X.vue'
5. relative imports            import { y } from './utils'
```

## Consequences

A strict order means reorganising imports in older files when they are next touched,
which produces occasional noisy diffs.
