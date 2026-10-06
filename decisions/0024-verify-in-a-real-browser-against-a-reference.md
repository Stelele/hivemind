# 0024. Verify in a real browser, against a reference

**Status:** accepted
**Date:** 2026-10-06
**Affects:** every frontend project

## Context
2026-04-14 — "you have access to the chrome mcp so test it out to see if its working as expected after your fixes" · 2026-05-12 — "can you test them with a real browser ui, you can use the images in the picturs folder for reference."

## Decision
A passing build is not verification. Open UI work in the browser and check it against reference material or documented behaviour.

## Consequences
Real defects get caught before you claim done. The cost is browser tooling must be available, and it is slower than a build.
