---
id: 20261024-1459-verify-modalities-metadata-before-routing-vision
title: Verify modalities metadata before routing vision roles
kind: lesson
topics: [ai, model-routing, agents]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-24T14:59+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
Rewiring subagent cost routing, I picked `claude-haiku-5-5` for the vision/screenshot-extraction agent by name association ("Claude = vision") plus decent per-token cost. The user pointed out GLM Flash and DeepSeek variants are also multimodal. Catalog check confirmed `glm-5.3-flash` accepts text/image/video/pdf and `deepseek-v4.1-flash` accepts text/image — both with 4–5x the monthly dollar cap of Haiku, at equal or cheaper rates. My choice was strictly worse on every measurable axis for the role.

## What we decided
Check `modalities.input` in the https://models.dev/api.json catalog before routing any model to an image/screenshot role — never route vision on name, family, or vendor folklore.

## Why
Model capability metadata is machine-readable and authoritative; assumptions are how the worst option gets picked silently. Also the same dump carries per-model `cost` and context limits, so one fetch settles the whole routing decision. A free variant with no `modalities` entry must be left as "unverified — confirm before use", not assumed either way.

## The cost
One extra HTTP fetch and a metadata read per routing decision (~seconds). Ids also drift from reality: a `-vl` suffix or a vendor's reputation can be stale, and the `vision` naming may simply be absent from a multimodal id (e.g. GLM Flash). Accepting that, routing tables gain one verification step and lose a class of silent mis-routing.
