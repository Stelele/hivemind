# 0045. Keep fixer prompts to 8 edits or fewer
**Status:** accepted
**Date:** 2026-10-06
**Affects:** opencode-config

## Context

Fixer agents were hitting step limits on batches of 10 or more edits.

Step budget scales with the number of distinct decisions in the prompt, not the number of
lines. Exact strings remove the re-reading that inflates it.

## Decision

Keep fixer prompts to **8 edits or fewer**, and quote the exact string to replace. Longer
batches exhaust the agent's step budget mid-fix.

## Consequences

More, smaller dispatches. Batch by concern rather than by file count.
