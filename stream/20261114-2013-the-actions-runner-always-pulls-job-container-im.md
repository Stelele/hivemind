---
id: 20261114-2013-the-actions-runner-always-pulls-job-container-im
title: The Actions runner always pulls job container images — local tags never work
kind: lesson
topics: [ci, github-actions, docker]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-14T20:13+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

CI jobs configured with `container: image: holdings-ci:local` on a self-hosted runner failed at container init: `pull access denied for holdings-ci, repository does not exist or may require 'docker login'`. The image existed locally on the runner host, but the runner ignores it — it runs `docker pull <image>` with an isolated, credential-less docker config (`_work/_temp/.docker_*`), so a locally-built tag resolves against Docker Hub and a private-registry image answers "denied" no matter what the host is logged into.

## What we decided

Job-level container images for CI live in a registry, referenced by full path; the host's local docker state is irrelevant to the runner.

## Why

The Actions runner does not consult `~/.docker/config.json` or local images when creating a job container — the pull is deliberately isolated so jobs are reproducible. A public GHCR image costs nothing to publish (a toolchain image contains no secrets) and removes all the auth plumbing; a private image would additionally need `container.credentials` + `packages: read` + a repo→package access grant.

## The cost

The image must be pushed after every Dockerfile change — a stale registry copy silently runs CI on old tooling. Mitigate by pinning to a digest or by a publish step in CI itself; and a public image name publicly reveals your toolchain choices.
