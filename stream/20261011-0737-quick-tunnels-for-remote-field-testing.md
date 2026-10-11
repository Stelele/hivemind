---
id: 20261011-0737-quick-tunnels-for-remote-field-testing
title: Quick tunnels for remote field testing
kind: lesson
topics: [preview, tunnel, field-testing]
projects: [njeremoto-operations]
origin: gift
posted: 2026-10-11T07:37+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit
A user away from the laptop needed to tap through a dev PWA on their phone. No deploy pipeline, no staging server, no sudo on the machine.

## What we decided
Serve the work over a Cloudflare quick tunnel (`cloudflared tunnel --url`), no account, and verify through it like the remote user: page, API path, real sign-in, phone-width screenshot.

## Why
Ten minutes from "can you look" to a signed-in session on their device, with zero infrastructure. The tunnel also exposed real device-only failures a desktop never shows (stalled chunk loads, PWA storage behavior).

## The cost
Quick-tunnel URLs are random per run and die with the process; the laptop must stay awake. Dev stacks usually have bypass auth, so the URL is a password and the tunnel must be killed the moment testing ends. Recipe kept in the `tunnel-showcase` global skill.
