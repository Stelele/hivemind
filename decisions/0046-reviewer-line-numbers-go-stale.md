# 0046. Reviewer line numbers go stale
**Status:** accepted
**Date:** 2026-10-06
**Affects:** opencode-config

## Context

Reviewer reports referenced line numbers that no longer matched the file after intervening
edits, so applying their suggestions corrupted the source.

Reviewers reason over a snapshot. By the time you act, that snapshot is stale — especially
in a multi-agent loop where a fixer has already edited the region.

## Decision

Always adjudicate a review against the **current** source before applying anything. Check
that the target line still contains the content the reviewer described.

## Consequences

An extra verification step per finding. Skipping it means the reviewer becomes a source
of bugs rather than a source of fixes.
