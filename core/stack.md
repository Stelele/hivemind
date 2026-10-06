# Stack

## Deployable work is Vue 3 + TypeScript in front, .NET 10 behind

The recurring application shape: Vue 3 + TypeScript (Vite, Pinia, Tailwind, `@nuxt/ui`)
frontend, .NET 10 backend (Minimal API, EF Core, CQRS/MediatR). Reuse this shape unless the
project already committed to something else.

*Evidence: consistent across cms-system, erpnext-dashboard, njeremoto-operations,
class-booking-system, personal-site, erpnext-cashbook-reconciliation.*
→ [ADR 0019](../decisions/0019-deployable-work-is-vue-3-typescript-and-net-10.md)

## Pick the database by job, not by habit

Not one database everywhere. Observed, with reasons:

| Project | Database | Why |
|---|---|---|
| cms-system backend services | SQLite | "I just want the @cms-system/backend/Api/ service to now use sqlite" — local/app data, no concurrent write pressure (2026-04-21) |
| pesepay-payment-gateway | PostgreSQL | "I'll go with postgres instead of sqlite. I want you to use the built in queue system that postgres offers" — needed its queue (2026-05-24) |
| erpnext-dashboard backend | PostgreSQL | multi-service, caching decorators, background workers |
| erpnext-cashbook-reconciliation | SQLite (node) | single-file reconciliation tool |

**The pattern:** use the database's capability that you are actually relying on, and say
which one you relied on. "We use X because it gives us Y" is the answer that survives review.
→ [ADR 0020](../decisions/0020-pick-the-database-by-job-not-by-habit.md)

## Use the platform capability rather than a hand-rolled one

Where a managed service or platform primitive already exists, use it instead of writing the
equivalent. Cloudflare R2 for object storage rather than a self-managed bucket layer.

*Evidence: 2026-06-24 — "lets go with hosting on cloudflare R2, I've got a public bucket
there already."*
→ [ADR 0021](../decisions/0021-use-the-platform-capability-not-a-hand-rolled-one.md)

## Frappe/ERPNext work follows Frappe's own layout

`hooks.py`, a proper Python package layout, whitelisted API functions inside an `api/`
module. Note that `frappe.call` paths include the module segment —
`frappe.call("my_app.api.my_function")`, not `frappe.call("my_app.my_function")`.

*Evidence: `awesome_restaurant3/AGENTS.md`, `.field-guide/index.md`, 8 sessions in
frappe-offline and frappe-bench.*
→ [ADR 0022](../decisions/0022-frappe-work-follows-frappe-s-own-layout.md)

## Skill conventions

Skills use `name` + a trigger-rich `description` in the YAML frontmatter and nothing else —
no `license`, no `allowed-tools`, no `metadata`. Descriptions enumerate concrete trigger
phrases because they are what actually get matched.

*Evidence: `~/.config/opencode/skills/{swarm,team,dotfiles,using-swarm}/SKILL.md`.*
→ [ADR 0023](../decisions/0023-skill-conventions.md)

## Name the capability, then pick the database

### What I hit

The payment gateway needed a queue. I was about to default every new backend service to
the same database the other services use, which is SQLite.

### What we decided

Name the capability you are relying on, then pick the store that provides it.

```
needs postgres queue      -> postgres
local app data, no writes -> sqlite
```

For pesepay-payment-gateway the answer was postgres, explicitly for its built-in queue
system. For the cms-system backend services it was SQLite, because nothing there needs
concurrent writes.

### Why

"We use X" is not a decision. "We use X because it gives us Y" survives review, and the
next person can tell whether Y still holds.

### The cost

A mixed estate. Two dialects of SQL to maintain, and the choice has to be re-litigated per
service instead of following a single house default.
