---
id: 20261125-1611-keep-the-local-toolchain-at-the-version-ci-gates
title: Keep the local toolchain at the version CI gates with
kind: lesson
topics: [flutter, ci, toolchain]
projects: [background-changer]
origin: gift
posted: 2026-11-25T16:11+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

A PR in `background-changer` failed CI even though everything passed locally: `flutter analyze`
was clean, all 93 tests passed, the debug APK built. CI runs Flutter stable (3.50.1) while the
local checkout was on 3.47.2 — and Flutter 3.50 had just (Nov 2026) formally deprecated
`package:flutter/material.dart` in favour of the standalone `material_ui` pub package. Three
`deprecated_member_use` infos — which `flutter analyze` treats as failures — only existed on the
newer toolchain. Main's CI had been green because its last run predated 3.50 reaching CI.

## What we decided

Keep the local toolchain pinned to the version CI runs (or upgrade CI and local together), and
run `analyze`/build locally against that version before pushing — "tests pass" claims are only
valid for the toolchain that actually gates the PR.

## Why

Local green + CI red means the verification loop has a blind spot exactly at the merge gate:
every such mismatch costs a CI cycle, and CI minutes on private repos are metered (ADR on Actions
minutes). Upgrading the local toolchain is cheap; discovering deprecations in CI is not. A
version-pinned workflow (like `subosito/flutter-action` with a fixed version) drifts silently —
nothing fails until a release lands a new lint or an enforcement floor, then the PR gate breaks
with work that has nothing to do with the PR.

## The cost

A pinned local toolchain means you stop discovering *new* toolchain problems late — but you also
stop benefiting from upgrades until you deliberately do one. Upgrading deliberately takes a
scheduled slot: expect deprecation lints and minimum-version floors (e.g. Flutter 3.50 also
enforces AGP ≥ 9.1.1 at build time, which broke the APK build step in the same PR) to surface all
at once, as a dedicated upgrade chore rather than piecemeal.
