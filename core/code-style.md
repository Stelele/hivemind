# Code style

## No non-null assertions — make the types specific instead

`!` used to silence a nullable type is a bug marker, not a fix. When you find them,
widen the type at the source instead of asserting at the point of use.

*Evidence: 2026-05-17 — "there's too much abuse of ! for enforcing a type is not null, the
type files have been updated to be more specific so this isn't necessary anymore, can you
clean it all up."*
→ [ADR 0007](../decisions/0007-no-non-null-assertions-widen-the-type.md)

## Flat response DTOs — no inheritance chains, no cycles

Response DTOs are flat structures built for the response. Do not build an inheritance
hierarchy of extended DTOs, and do not let a response reference an object that points
back (e.g. `CompanyResponse → site → companyId`). A request object is not the same thing
as a command — do not reuse it as one and call it a day.

*Evidence: 2026-06-07 — "there's a lot of unnecessary inheritance and creating many
extended DTOs for responses that really have no right to be there… I made a dumb decision
of directly putting the command as the api request object instead of a proper request
object leading to weird duplication." · 2026-06-08 — "there's an element of clyclical
duplication like CompanyResponse -> site -> companyId. this doesn't make sense in the
context of the response."*
→ [ADR 0008](../decisions/0008-flat-response-dtos-no-inheritance-no-cycles.md)

## Delete dead code when the feature is done

When a feature lands and code it replaced is now unreachable, remove the dead code. Do not
leave it "just in case", and do not leave unused exports, variables or whole files.

*Evidence: 2026-04-16 — "now I want to remove the unused code since we're now done."*
→ [ADR 0009](../decisions/0009-delete-dead-code-when-the-feature-is-done.md)

## DRY, but separation of concerns wins ties

Apply the pragmatic engineer's reading of DRY: remove genuine duplication, but do not merge
things that are separately meaningful just because their bodies look alike.

*Evidence: 2026-04-16 — "minor refactoring so we honer the pragramtic engineers principle of
DRY and appropropriate sepation of concerns." · 2026-05-22 — "thats also duplication, can you
help me consolidate the logic between the two functions."*
→ [ADR 0010](../decisions/0010-dry-but-separation-of-concerns-wins-ties.md)

## No over-assertion on optionality

Prefer returning absent/optional over inventing a sentinel value. `null`/`undefined` is an
acceptable answer; a magic default that silently becomes real data is not.
