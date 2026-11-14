# 0057. Jev screen default flipped to ON (per-repo opt-out) — opt-in made the default the expensive path
**Status:** accepted
**Date:** 2026-11-14
**Affects:** ocr-review

## Context

The Jev noul screen for the OCR verdict sweeper shipped as per-repo opt-in
(VERDICT_JEV_SCREEN=true). That made the DEFAULT path for all 110 repos the expensive
one: every lingering thread paid a ~15-20s glm-5.3-flash call that the calibrated screen
would have decided for free in a batched sub-second request.

The opt-in was justified while the thresholds were unproven. After the calibration
(15 labeled threads: 0/9 false resolves; 3 "misses" were contestable labels) and the
594-thread backlog replay (0.8 min, $0, 0 failures, 2/2 mechanical spot-checks against
the resolve record), plus the security hardening rounds, the caution was spent and the
default was simply the worse configuration.

## Decision

The screen is ON by default; a repo opts out with VERDICT_JEV_SCREEN=false (0/no/off
accepted). All safeguards unchanged: no token, a non-opencode stage-2 provider without an
explicit JEV_TOKEN secret, fork PRs, and a moved head auto-disable the screen and fall
back to the reasoning LLM.

## Consequences

- Default-on means the free tier now serves the whole account: sustained per-PR volume
  is untested beyond the 525k-token replay; if the free tier throttles, the screen
  fails closed to the reasoning LLM (cost, not breakage), and a paid jev-1.13 needs
  Console credits.
- Auto-resolution of low/medium findings now happens account-wide on merge rather than
  repo-by-repo decision; wrong auto-resolves are reversible (unresolve) but happen
  without a per-repo human first-run.
