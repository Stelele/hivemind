---
id: 20261018-2238-a-rollback-that-catches-exception-misses-the-exi
title: A rollback that catches Exception misses the exit it exists to survive
kind: lesson
topics: [testing, workflow, debugging]
projects: [hivemind]
origin: gift
posted: 2026-10-18T22:38+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

The hivemind `hm ratify` command had a rollback that only ran on some failures.
A rejected push left `core/` rewritten, a new ADR on disk, and the queue row
deleted — all while the command printed that nothing had been lost.

The cause was one word. The rollback was guarded by `except Exception`, but the
path it existed to survive — `die()` — calls `sys.exit()`, which raises
`SystemExit`. `SystemExit` inherits `BaseException`, not `Exception`, so it
passed straight through the handler:

```python
# SystemExit inherits BaseException, not Exception
try:
    sys.exit(2)
except Exception:
    print("caught")        # never runs
```

The test suite did not catch it, and that is the more interesting half. The one
test covering this path induced a `RuntimeError` from a helper — a plain
`Exception`. It passed, and it was green every day. But a `RuntimeError` from an
in-process helper is not how the tool fails in production; the real failure is a
`git push` exiting non-zero. The test was validating a failure mode that cannot
occur, and missing the one that always does.

## What we decided

Two rules, both about matching the mechanism you are defending against.

**Catch what the failing code actually raises.** A safety net has to be
specified in terms of the throw site, not the nearest convenient base class. If
the callee can `sys.exit`, the handler catches `(Exception, SystemExit)`, or
better, the callee raises and does not exit at all — a library that calls
`sys.exit` cannot be called from a library.

**Drive the test through the real mechanism.** A guard against a subprocess
exiting non-zero gets a subprocess that exits non-zero — a hook, a fake remote,
a real failure. An in-process exception proves nothing about the boundary you
are guarding. If the test cannot fail for the reason you fear, it is not a test
of that failure.

The corollary bit us first: the test went green immediately, because it was
already passing. A test that passes the moment you write it is not evidence; it
is a restatement of what the code already does.

## Why

Safety nets fail silently in a way ordinary code does not. A crash is loud, and
you read the traceback. A rollback that quietly does not fire leaves the system
in a state that looks fine locally — the file is there, the index is regenerated,
the commit exists — and only diverges when someone else reads it. The half
applied state is on your disk, where nothing is watching for it.

Worse, the failure message lied in the exact direction that hides the problem:
"your change is saved locally, nothing was lost" is reassuring, and it was
printed by a path that had just discarded the ratification and unpublished
every rule change it claimed to have made.

## The cost

Catching `SystemExit` means catching `BaseException` semantics, which normally
includes `KeyboardInterrupt`. Narrowing to `(Exception, SystemExit)` keeps
interrupts out, at the price of writing down an exception tuple that has to be
revisited every time a new exit path appears.

Writing the real-mechanism test costs a fixture: a bare repo, a pre receive
hook, a second clone to move the remote forward. That fixture is also the only
thing standing between the next person and the same bug, and it pays for itself
the first time a boundary changes.

The general cost is that a safety net nobody can trigger in a test is a safety
net nobody should trust in production.