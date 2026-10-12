---
id: 20261012-1913-settle-sync-draining-e2e-on-outbox-truth-not-cli
title: Settle sync-draining e2e on outbox truth, not clicks
kind: lesson
topics: [playwright, e2e, offline-sync]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-12T19:13+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
E2e sync tests flaked three different ways that all looked like product bugs: entries missing from
the server after a green sync icon, queues stuck with one row for a full minute, saves vanishing
without a trace. Every one was the harness, not the app: clicking "Sync now" resolves its requester
even when the run is dropped (one already in flight), and navigating or reloading mid-push strands
the claimed outbox row until the 60s claim lease expires — with nothing re-triggering it headless.
## What we decided
Settle on outbox truth, not clicks or icons: after triggering a drain, poll until no pending or
sending row remains (rows held back by a blocked day excluded, keyed the way the drain keys them),
and only then reload or assert. Never navigate between a save click and the queued row's appearance.
## Why
The icon can read settled while rows are mid-push, and a reload mid-push guarantees a stuck row.
Polling the outbox distinguishes "drained" from "asked", and the blocked-day exclusion keeps
conflict scenarios settleable. Three mystery failures across two suites vanished with no product
change once the harness stopped racing the drain.
## The cost
Slower tests: each settle spends a 4s poll loop and survives a full claim lease (~65s) before
failing, so a genuinely wedged queue costs three minutes to report instead of thirty seconds.
