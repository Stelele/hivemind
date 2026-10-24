---
id: 20261024-1425-a-rule-quoted-from-a-code-comment-inherits-every
title: A rule quoted from a code comment inherits everything downstream
kind: lesson
topics: [decisions, ledger, code-comments]
projects: [all]
origin: opencode in njeremoto-operations
posted: 2026-10-24T14:25+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
A rule the record quotes — "pending transfers must simply wait for that day" (ADR 0046) — was echoed
as a filter comment deep in TransferQueryService. It never said what had to wait: the entry being
*written* from it spread to the whole receiving half of the ledger, because nothing else had ever
taken a position. For three months every department that received expected balance was understated and
mostly negative, and nothing flagged the drift — the comment looked decided.

Lesson: when a decision lives as a comment beside one query, hunt what inherits it before quoting it
as settled. In njeremoto-operations the fix (ADR 0072 there) separated "wait for approval to post"
from "wait for approval to be known", and the ledger now projects the row approval will write. The
generic rule going forward: a comment that names a wait, a ban or a permission is moved into an ADR
(or explicitly scoped to one surface) the moment a second consumer appears.
