---
id: 20261024-1840-dexie-vue-refs-clone-before-writing-real-indexed
title: Dexie + Vue refs: clone before writing — real IndexedDB refuses proxies
kind: lesson
topics: [vue, dexie, pwas, testing]
projects: [njeremoto-operations]
origin: opencode session (GLM-5.3-flash), njeremoto-operations e2e debug
posted: 2026-10-24T18:40+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Dexie writes in a Vue component must not receive a component `ref`'s contents directly.
`ref()` deep-wraps any value assigned to it in reactive proxies, and `{ ...proxy }` spreads
copy top-level keys only — nested arrays and objects (a batch's `lines`, a diary entry's
photos) stay **proxies**. Real Chromium's IndexedDB refuses to structured-clone a proxy and
answers with `DataCloneError: [object Object] could not be cloned`; `fake-indexeddb`, the test
environment, accepts them silently, so 441 green unit tests and a blue CI prove nothing here.

The failure shape is the nastiest kind: the optimistic write happens *after* the server call
has already succeeded, so the user sees a red "That action could not be completed." banner
over an action that worked — the server and the device disagree about who errored.

**Rule:** every mirror write handed from component code goes through a `JSON.parse(JSON.stringify())`
clone at the Dexie boundary (see `applyLocal` in `BatchDetailView.vue`), and a contract test
asserts the handed structure is not reactive (`isReactive` false on the row, its arrays, its
entries). The energetic alternative — chasing the throw through a 10-minute e2e with the trace's
network file naming the exact `IDBObjectStore.put` — is how this was found; the pl_state lesson
is to never hand a Dexie call an object that has been inside a `ref`.