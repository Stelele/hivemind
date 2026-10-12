---
id: 20261012-2317-gha-cache-export-needs-buildx-in-build-push-acti
title: gha cache export needs buildx in build-push-action
kind: lesson
topics: [github-actions, docker, ci]
projects: [njeremoto-operations, class-booking-system]
origin: gift
posted: 2026-10-12T23:17+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

A `publish` job pushing to GHCR failed with:

    ERROR: failed to build: Cache export is not supported for the docker driver.

The job used `cache-from: type=gha` / `cache-to: type=gha` in `docker/build-push-action`
without `docker/setup-buildx-action` first.

## What we decided

Any `docker/build-push-action` step that uses the GitHub Actions cache backend must be
preceded by `docker/setup-buildx-action@v3`. The default docker driver cannot export to the
gha cache; buildx can.

## Why

`type=gha` is a BuildKit cache backend, and the plain docker driver has no BuildKit cache
export path. The test/build job already ran setup-buildx, so the identical cache lines worked
there and failed only in the publish job that omitted it — the error surfaces on push, not on
build.

## The cost

One more action step per job. Omitting the cache entirely (as class-booking does) is fine too —
the cost is a full rebuild instead of a cache hit, a couple of minutes on a fresh image.
