# 0031. User-facing prose must not leak implementation detail

**Status:** accepted
**Date:** 2026-10-06
**Affects:** personal-site, any docs or blog

## Context
2026-10-04 — "your writing doesn't sound like a blog post. you're talking too much about specific filenames. no one is gonna read the code and it only makes sense to me. remember these are blog posts meant to help someone understand the project that very likely won't look at the code."

## Decision
No filenames, class names or diffs in text a non-project reader sees. Write in the register of an engineering blog — explain the problem and the shape of the fix.

## Consequences
Content is readable by its actual audience. The cost is vaguer writing; internal comments must still be precise.
