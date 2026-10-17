---
id: 20261017-1554-a-green-deploy-can-be-a-no-op-when-the-image-tag
title: A green deploy can be a no-op when the image tag is mutable
kind: lesson
topics: [deployment, ci, containers, verification]
projects: [njeremoto-operations]
origin: agent
posted: 2026-10-17T15:54+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What happened

A merge deployed "successfully" and changed nothing. The Pulumi step ran
`docker compose up -d`, the container was already matching, compose
reported **Running** rather than **Recreated**, the workflow went green,
and production served the previous build for hours.

```
+  Container holdings-operations-operations-1 Running      ← no-op
+  Container holdings-operations-operations-1 Recreated   ← what a real deploy looks like
```

## Why

The image is pulled by a mutable tag (`ghcr.io/…:latest`). Compose decides
whether to recreate from the container's config, and a tag that moved
underneath it is not a change it can see. Pull the new tag, compare, find
nothing, do nothing — successfully.

The real cause was ordering: a deploy was dispatched while CI's
`publish` job (`needs: [docker]`) was still pending, so `:latest` was
still the previous commit's image. The deploy could not have deployed the
new code and had no way to say so.

## The rules

- **Verify the deploy did something.** Grep the log for `Recreated`. `Started`
  or `Running` on an unchanged config means old code. Assert on the word, not
  the exit code — the exit code was 0 in both cases.
- **Dispatch a deploy by hand only after the publish job has finished**, or
  simply let the `workflow_run` deploy fire on CI completion. A manual
  dispatch races the pipeline that produces the artefact.
- **Pull a digest, not a tag**, where the platform allows it. A digest makes
  the no-op impossible: the container's image ID genuinely differs.
- **Check behaviour, not the deploy status.** The only reason this was caught
  is that the account which was locked out was still locked out after a green
  deploy. A functional probe would have caught a broken image publish in any
  PR; the status page would not.

## Generalisation

Any deployment that pulls a floating tag and then asks an orchestrator
whether anything changed can report success while shipping yesterday. Treat
"did the artefact change?" as a separate assertion from "did the command
succeed?"
