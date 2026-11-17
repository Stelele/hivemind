---
id: 20261117-1026-new-fedora-runner-hosts-check-vfree-before-first
title: New Fedora runner hosts: check VFree before first CI; Actions run-creation stalls are diagnosable via check-suites
kind: lesson
topics: [linux, lvm, github-actions, ci]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-17T10:26+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Two separate, easily-conflated capacity incidents on the same day, both in the new laptop CI runner's first real production run on njeremoto-operations:

1. Fedora Server's installer put the system on a **15 GB root LV out of a 236 GB NVMe** — ~220 GB sat unallocated in the volume group, unmounted and invisible to `df`. The first full CI run (docker buildx export + a parallel e2e stack) died with `no space left on device` at 43 MB free, in two different jobs at once, reading exactly like resource contention.
2. Interleaved with that, GitHub Actions **stopped creating runs** for the repo twice (multi-hour gaps): pushes were delivered (third-party check apps like GitGuardian created check-runs), workflows were `active`, status page said all-healthy — but zero runs were created, in-flight runs kept executing. Run creation resumed on its own, then dropped again, then resumed.

## What we decided

On any new Fedora/LVM runner host, immediately after install run `sudo vgs` — if `VFree` is large, `sudo lvextend -l +100%FREE /dev/mapper/<vg>-root && sudo xfs_growfs /` before the first CI run; do not trust the installer's partitioning, and do not trust a photo of `df` read over the shoulder. When Actions runs stop being created despite delivered pushes, query `actions/runs?head_sha=<sha>` and `commits/<sha>/check-suites` (Actions app absent = run-creation stall, not workflow misconfig), retrigger with an empty commit, and treat the in-flight runs as unaffected.

## Why

Both failures mimic something else: disk exhaustion inside one lane reads like the same-host e2e contention flakes, and the run-creation stall reads like a workflow bug or a billing gate. The check-suite query is the discriminator that costs ten seconds; the `vgs` check is the one command that would have saved a red production run. Conflating "two jobs failed at once" with "concurrency flakes" would have sent us chasing the wrong fix (de-labelling lanes) while the actual disk was 43 MB from full.

## The cost

The LV extension must happen before heavy use or a run dies mid-build; the check-suite/head_sha diagnostic adds a step to every "why is CI not starting" investigation instead of just re-pushing. And `df` read from an install-day photo is now banned as evidence — the numbers were misread once, at scale.
