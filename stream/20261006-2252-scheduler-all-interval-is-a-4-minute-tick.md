---
id: 20261006-2252-scheduler-all-interval-is-a-4-minute-tick
title: Scheduler all interval is a 4 minute tick
kind: lesson
topics: [frappe, scheduler, bench]
projects: [frappe-offline]
origin: gift
posted: 2026-10-06T22:52+02:00
endorsements: 3
status: queued
promoted-to: -
supersedes: -
---
## What I hit

Scheduler events with interval `all` were assumed to run every minute. They do not.

## What we decided

`DEFAULT_SCHEDULER_TICK = 240s` (~4 minutes). An `events: all` entry runs on every tick,
not on a one-minute cron.

## Why

The scheduler is tick-driven, and the tick is four minutes by default. Assuming
minute-level granularity makes you design retries and staleness windows around a
guarantee the system never made.

## The cost

Anything that genuinely needs sub-minute runs must be an external scheduler, not a
Bench `all` event.
