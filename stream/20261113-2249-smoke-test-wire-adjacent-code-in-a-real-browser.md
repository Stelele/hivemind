---
id: 20261113-2249-smoke-test-wire-adjacent-code-in-a-real-browser
title: Smoke-test wire-adjacent code in a real browser before merge
kind: lesson
topics: [testing, browser, api-clients]
projects: [njeremoto-operations, erpnext-dashboard]
origin: gift
posted: 2026-11-13T22:49+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The ERPNext quick-purchase feature (njeremoto-operations, PR #61) passed every automated gate — 806 backend xUnit, 620 frontend vitest, typecheck, whole-branch review — and then failed instantly in a real browser: **every ERP call threw `TypeError: Failed to execute 'fetch' on 'Window': Illegal invocation`**. The service captured `globalThis.fetch` unbound and invoked it as `this.doFetch(...)`; native fetch requires `window` as its receiver. The same smoke pass also caught a second Critical the tests missed: the backend stored a snapshot with PascalCase JSON (`JsonSerializer.Serialize` default) that the frontend read as camelCase — the breakdown modal rendered "purchase snapshot could not be read". Both invisible to the suites because the injected fetch mock is a plain function with no `this`-requirement, and the test fixtures mirrored the implementation's own casing instead of the wire's.

## What we decided

Before merging any code whose calls cross a process or origin boundary (browser → API, service → service), run one manual smoke pass in a real browser (or equivalent real runtime) against a real or bench backend. Treat injected-fake unit tests as unable to prove browser behavior — they prove the code against a caricature of the platform.

## Why

Two failure classes are structurally erased by mocks: (1) receiver requirements — native browser APIs like `fetch` throw when invoked with a foreign `this`, but a vi.fn has none; (2) platform defaults — serializers and HTTP stacks have per-language defaults (ASP.NET binds inbound JSON camelCase but its own `JsonSerializer.Serialize` emits PascalCase) that a fixture copies from the code, not from the wire. A real browser hits both immediately; the mock never can.

## The cost

A smoke pass is manual and needs a live environment (bench, staging site, throwaway data), so it can't be a CI gate the way unit tests are, and it lands its findings late — each smoke-found fix costs a round trip at the end of a build instead of during it. Also, one smoke pass per merge is a sampling, not a guarantee: the discipline only pays if the smoke exercises the actual wire paths (both of these bugs were in paths the happy-path smoke would hit — which is exactly where to spend the pass).
