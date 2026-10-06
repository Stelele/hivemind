# Architecture

## Verify against real documentation before implementing

Do not implement from recollection. Fetch and read the actual docs — via the browser MCP if
that is what it takes — and read the framework's own codebase for the established pattern.
If the docs do not mention the feature you were about to build, that is the answer.

*Evidence: 2026-06-09 — "I'm pretty sure you're overcomplicating things. read the erpnext
docs and codebase on how to do this for api server scripts." · 2026-06-02 — "if you read the
docs via the chrome mcp you'll see it doesn't talk about webhooks at all." · 2026-06-01 —
"read the docs again."*
→ [ADR 0011](../decisions/0011-verify-against-real-documentation-before-implementing.md)

## Simplicity outranks resilience when volume does not justify it

Fault tolerance, queues and retry machinery must be justified by the actual transaction
volume. Building it for volume that does not exist produces a service that is hard to read
and impossible to reason about, and the resilience buys nothing.

*Evidence: 2026-06-02 — "the current service is heavily over engineered to thee point of
being useless. All I really care about is the raw payment and the things like fault tolerance
and such don't make sense considering the current transaction volume which is quite literally
non existent."*
→ [ADR 0012](../decisions/0012-simplicity-outranks-resilience-when-volume-does-not-justify-it.md)

## Maximum performance is the end result when asked for it

When the stated goal is performance, do not trade it away for tidiness without saying so.
Choose the fast option, and record the trade-off.

*Evidence: 2026-04-15 — "no I want maximum performance as the end result." Repeated
latency complaints follow: 2026-06-10 — "no thats too slow that fetch all runs every 5min
whoo'se gonna wait for that."*
→ [ADR 0013](../decisions/0013-maximum-performance-is-the-end-result-when-asked-for-it.md)

## Err toward reliability, but within reason

Default to the more reliable option when choices are close — but "reliable" never justifies
unbounded complexity. Say which way you went and why.

*Evidence: 2026-05-24 — "I'd err more towards reliability within reason so lets go with C."*
→ [ADR 0014](../decisions/0014-err-toward-reliability-within-reason.md)

## Keep changes narrowly scoped

Do not sweep the codebase when the fix is local. A change that "had to" touch twenty files
is almost always solving the wrong problem, or a problem that was not asked for.

*Evidence: 2026-06-13 — "there's no reason to do such a large sweep of all the files and the
file name is not guaranteed."*
→ [ADR 0015](../decisions/0015-keep-changes-narrowly-scoped.md)

## Compute presentation concerns on the client

Date-range arithmetic, grouping and bucketing that exist purely to render a view belong in
the frontend. Send the backend the actual ranges to query, not pre-grouped display buckets.

*Evidence: 2026-04-15 — "do the date range calculations start, end, grouping etc in the
frontend then pass the actual date arrays to the backend function."*
→ [ADR 0016](../decisions/0016-compute-presentation-concerns-on-the-client.md)

## Restraint in the UI

Fewer controls on screen beat more. When two elements compete for the same space, remove
one rather than splitting the difference.

*Evidence: 2026-06-06 — "also the avatar badge so that we only leave one thing on the right
to prevent overwelming the ui."*
→ [ADR 0017](../decisions/0017-restraint-in-the-ui.md)

## Explicit save over autosave

Autosave that fights the user is worse than a save button. Prefer one explicit save action
in line with the thing being saved.

*Evidence: 2026-07-20 — "this is becoming an annoying feature and becoming overly complicated.
lets remove the autosaving feature completly. instead, lets have a dedicated save button in
the same line."*
→ [ADR 0018](../decisions/0018-explicit-save-over-autosave.md)

## App name is not the folder name

### What I hit

`bench get-app` creates a folder whose name does not match the app's Python module name,
so imports and `hooks.py` references end up wrong.

### What we decided

Check `hooks.py` or `setup.py` for the canonical `app_name` before referencing anything.
Real example: repo folder `awesome_dashboard_scripts` → `app_name` `awesome_dashboard`.

### Why

The folder is a checkout location. The app name is what Frappe routes, installs and
imports on.

### The cost

You cannot infer one from the other. Reading one line of config beats guessing every time.

## frappe.call endpoints need the .api module segment

### What I hit

Workers kept calling `frappe.call("pos_expenses.get_expenses")` and getting a 404. The
endpoint path is missing its module segment.

### What we decided

`frappe.call` paths include the `.api` module segment. Always verify the module-level
`__init__.py` exports against actual `frappe.call` usages before referencing an endpoint.

```python
frappe.call("pos_expenses.api.get_expenses")     # correct
frappe.call("awesome_dashboard.api.get_data")    # correct
frappe.call("pos_expenses.get_expenses")         # 404
```

### Why

The Python module path and the RPC path are not the same thing. Frappe routes by dotted
path, so the endpoint has to mirror the package layout.

### The cost

An extra lookup before every cross-app call. If you assume the layout instead of
checking, you burn a debugging cycle instead.

## Bench CLI verbs that do not exist

### What I hit

Repeated failures from agents and workers invoking Bench commands that do not exist.

### What we decided

The real verbs are:

| Do not use | Use instead |
|---|---|
| `bench switch-to-version` | `bench switch-to-branch <branch>` |
| `bench run-app` | `bench start` |
| `bench run-app` | `bench set-config site developer_mode 1` |
| `bench run_tests` | `bench run-tests --app <app>` |

### Why

These three wrong verbs appeared often enough to be worth pinning. They read plausibly,
which is exactly why they keep being guessed.

### The cost

One more place to look up. `bench --help` is authoritative and should win over this post
if they ever disagree.

## Scheduler all interval is a 4 minute tick

### What I hit

Scheduler events with interval `all` were assumed to run every minute. They do not.

### What we decided

`DEFAULT_SCHEDULER_TICK = 240s` (~4 minutes). An `events: all` entry runs on every tick,
not on a one-minute cron.

### Why

The scheduler is tick-driven, and the tick is four minutes by default. Assuming
minute-level granularity makes you design retries and staleness windows around a
guarantee the system never made.

### The cost

Anything that genuinely needs sub-minute runs must be an external scheduler, not a
Bench `all` event.

## Page permissions beat JS role gates

### What I hit

A page rendered for the user while its JavaScript refused to act, producing a confusing
half-working UI.

### What we decided

Page-level DocType permissions and JavaScript role gates can diverge. **The page `perm`
wins at render time.** A user can see a page that JS then blocks, or fail to see a page
whose JS would have allowed it.

### Why

Rendering happens before any of your JS runs, so permission resolution cannot be undone
by a client-side check.

### The cost

Two systems to keep in sync, and the client-side one is advisory only. Treat JS role
checks as UX, never as authorization.

## Move dense controls into the drawer on mobile

### What I hit

Reworking the erpnext-dashboard mobile view. Two problems were tangled together: the nav
drawer, and reporting-period selection. The period control was a row of small slices and
users were misclicking them.

### What we decided

Move the period selector **into** the drawer rather than fighting it on the main surface.
One control, one place, larger tap targets.

```mermaid
mobile (< lg)
  ├─ top bar:        [☰] [period selector] [avatar]
  └─ drawer:         nav · logout · period selector
```

### Why

The misclicks were a symptom of control density on a small screen, not of the control
itself. Relocating it solved both problems at once instead of treating them separately.

### The cost

One fewer always-visible control, so the period is less discoverable on mobile. Accepted
in exchange for not shipping a control people misclick.

**Crosspost:** the same drawer-plus-relocated-settings shape is a reasonable default for
any Vue project's small-screen layout. Worth trying before hand-rolling a new nav.
