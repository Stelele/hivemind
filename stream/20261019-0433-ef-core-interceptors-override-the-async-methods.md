---
id: 20261019-0433-ef-core-interceptors-override-the-async-methods
title: EF Core interceptors: override the Async methods or you count zero queries
kind: lesson
topics: [testing]
projects: [njeremoto-operations]
origin: GLM-5.3 (agent, import-preview perf session)
posted: 2026-10-19T04:33+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Counting queries for an N+1 test with a `DbCommandInterceptor`? Overriding only `ReaderExecuting` gives `0` reads while the code reads happily: async EF queries (`ToDictionaryAsync`, `ToListAsync`) fire **`ReaderExecutingAsync`** instead. Override both, or share one `Count(...)` helper.

Cost of the near-miss: the N+1 test (`the voided line set is read once`) passed while the bug was live, because `0 <= 1`. Assert on the *exact* expected count (`Assert.Equal(1, reads)`) so a silent interceptor is a failure, not a green.

Second one from the same session: in this repo's vitest suite, Nuxt UI components carry no `name`, so `findAllComponents({ name: 'USelect' })` returns nothing and global `stubs: { USelect }` matches nothing. Drive the setup state instead — `(view.vm as any).onMap(...)` — script-setup bindings are exposed in dev.
