# Core — the always-read tier

Everything in `core/` is **ratified**. Treat it as law, not suggestion. Every rule here
has a numbered ADR in [`decisions/`](../decisions/) that records why, including the cost.

If a rule here conflicts with a project's own conventions, that is a bug — open a
`kind: question` post on the board rather than silently picking a side.

> **Read budget: this file plus 2–3 topic files. Never read all six.**

| If you are doing… | Read |
|---|---|
| anything code-related | [`code-style.md`](code-style.md) |
| Vue, Nuxt, Pinia, Tailwind, @nuxt/ui | [`code-style.md`](code-style.md) · [`stack.md`](stack.md) |
| C#, EF Core, MediatR, CQRS, Minimal API | [`architecture.md`](architecture.md) · [`stack.md`](stack.md) |
| Frappe / ERPNext, hooks.py, server scripts | [`architecture.md`](architecture.md) · [`stack.md`](stack.md) |
| designing or restructuring layers | [`architecture.md`](architecture.md) |
| picking a library or a database | [`stack.md`](stack.md) |
| deciding whether something is "done" | [`testing.md`](testing.md) |
| tests, CI, deploys, commits, branches | [`testing.md`](testing.md) · [`workflow.md`](workflow.md) |
| about to run git write commands | [`workflow.md`](workflow.md) |
| writing prose, docs, or asking a question | [`communication.md`](communication.md) |
| unsure | [`communication.md`](communication.md) — the fallback for anything ambiguous |

---

## The five that matter most

If you read nothing else, read these. They are the ones that get violated most:

1. **Never commit, push, or open a PR without an explicit instruction.** — [workflow](workflow.md#never-commit-push-or-open-a-pr-without-an-explicit-instruction)
2. **Make the change, then run the tests once.** Not per edit. — [workflow](workflow.md#batch-the-change-then-test-once)
3. **Check the real docs before implementing.** Do not work from recollection. — [architecture](architecture.md#verify-against-real-documentation-before-implementing)
4. **Show the reasoning and the instructions, not just the diff.** — [communication](communication.md#show-the-instructions-and-the-reasoning-not-just-the-diff)
5. **Simplicity outranks resilience when the volume does not justify it.** — [architecture](architecture.md#simplicity-outranks-resilience-when-volume-does-not-justify-it)
