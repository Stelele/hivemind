---
id: 20261015-2231-a-name-two-sides-each-derive-from-a-third-will-d
title: A name two sides each derive from a third will drift, and it drifts into silence
kind: lesson
topics: [naming, integration, archive, ef-core, single-source-of-truth]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-15T22:31+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Two halves of one system both needed to know where a department's archive day-files live. The archive
sync wrote them; the import preview read them. Neither stored the answer — each derived it from the org
unit's name, because that was the only department name either had.

The derivations disagreed. The archive repo spells the folder the way the estate says the department's
name (`Mugwawa`, `BroilerProject`, `OsmondResearch`); the org units carry the ledger names
(`Mugwawa Logistics Cash Book`, `Broiler Project`, `Osmond Research and Testing`). Five of nine
departments matched nothing, so their notes were filed under a name nothing ever searched for.

Nothing threw. The import simply found no notes for those departments and reported the books as having
zero. The receipts were the tell: all fifteen lived in the two folders that matched nothing at all.

## What we decided

Record the mapping once, in a table, and have both sides read it. Not "pick the better name and use it
everywhere" — that only works while the two spellings stay in step, and they are maintained by different
people for different reasons.

A department with no row falls back to its own name. Absence means "use the name", not "error", so a
department that keeps no archive folder keeps working.

## Why

The failure is silent by construction. Both derivations were individually reasonable and neither was
wrong about its own side — they were answering different questions from the same input, and the input
was the app's spelling rather than the archive's. Any disagreement between two independent derivations of
one fact surfaces as missing data, never as an exception, which is exactly why it survived.

Generalizable version: when two consumers each compute the same fact from a third value, the mapping is
going to drift, and it will drift into silence. Record the fact.

## The cost

The mapping has to be maintained. A department added later gets no row and silently becomes invisible
again — the same defect, reintroduced by omission. A seeder covers the known set, which hides the gap
rather than removing it.

Distinct from the older "app name is not the folder name" lesson, which is about reading one canonical
name instead of inferring it. This one is about two consumers agreeing, and the remedy is a shared
mapping rather than a single source field.
