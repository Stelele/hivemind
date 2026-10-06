# 0042. Scheduler all interval is a 4 minute tick
**Status:** accepted
**Date:** 2026-10-06
**Affects:** frappe-offline

## Context

Scheduler events with interval `all` were assumed to run every minute. They do not.

The scheduler is tick-driven, and the tick is four minutes by default. Assuming
minute-level granularity makes you design retries and staleness windows around a
guarantee the system never made.

## Decision

`DEFAULT_SCHEDULER_TICK = 240s` (~4 minutes). An `events: all` entry runs on every tick,
not on a one-minute cron.

## Consequences

Anything that genuinely needs sub-minute runs must be an external scheduler, not a
Bench `all` event.
