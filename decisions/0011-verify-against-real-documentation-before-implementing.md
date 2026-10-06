# 0011. Verify against real documentation before implementing

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every project

## Context
2026-06-09 — "I'm pretty sure you're overcomplicating things. read the erpnext docs and codebase on how to do this for api server scripts." · 2026-06-02 — "if you read the docs via the chrome mcp you'll see it doesn't talk about webhooks at all." · 2026-06-01 — "read the docs again."

## Decision
Fetch and read the actual docs before implementing, and read the framework's own codebase for the established pattern. If the docs do not mention the feature, that is the answer.

## Consequences
Far fewer confidently-wrong implementations. The cost is a network fetch and a slower first response.
