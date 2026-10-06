# Testing

## Verify in a real browser, against a reference

Do not declare UI work verified from a passing build. Open it in the browser via the
available browser tooling and check it against reference material — screenshots the user
has provided, a reference site, or the documented behaviour.

*Evidence: 2026-04-14 — "you have access to the chrome mcp so test it out to see if its
working as expected after your fixes" · 2026-05-12 — "can you test them with a real browser
ui, you can use the images in the picturs folder for reference."*
→ [ADR 0024](../decisions/0024-verify-in-a-real-browser-against-a-reference.md)

## Temporary tests to prove a path works are acceptable

When a feature has no test suite, write throwaway tests to prove the endpoints actually
work end to end, then decide with the user whether they stay. A claim of "it works" backed
by no execution is not verification.

*Evidence: 2026-05-12 — "you can write temporary tests to verify both the backup and upload,
get, delete file endpoints work and same for the database."*
→ [ADR 0025](../decisions/0025-temporary-tests-to-prove-a-path-works.md)

## Test frameworks per stack

| Stack | Framework | State |
|---|---|---|
| Vue / TS frontends | Vitest + Playwright | **Not yet installed** in most projects — the standing note is "when adding tests, use Vitest, use Playwright" |
| .NET | xUnit | used in PesePay |
| Frappe app | Cypress + pytest | used in `awesome_restaurant3` |

An absent test suite is not an excuse to skip verification — see the browser rule above.

*Evidence: `cms-system/frontend/AGENTS.md`, `personal-site/frontend/AGENTS.md` (both record
"no test framework currently installed"), `awesome_restaurant3/AGENTS.md`, PesePay.*
→ [ADR 0026](../decisions/0026-test-frameworks-per-stack.md)

## A review gate runs before you call it done

Work goes through a spec-compliance pass and a code-quality pass before completion. Both
are separate lenses and both must clear. This is the established pattern, not something to
invent per task.

*Evidence: repeated reviewer prompts across 2026-06-04 → 2026-06-07 in erpnext-dashboard,
each task getting a "review for spec compliance" and a "review for code quality" agent;
2026-07-29 — "fire indipendant review agents with different models to critic the website";
2026-08-05 — "fire two adeversarial agents to criticise the spec, one with vision
capabilities and one that looks up best practices".*
→ [ADR 0027](../decisions/0027-a-review-gate-runs-before-you-call-it-done.md)
