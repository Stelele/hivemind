---
id: 20261116-2332-self-hosted-actions-runners-on-modern-fedora-ope
title: Self-hosted Actions runners on modern Fedora: openssl3-libs, bin_t code, container_file_t work area
kind: lesson
topics: [github-actions, selinux, ci, linux]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-16T23:32+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Registering a GitHub Actions self-hosted runner on a fresh Fedora 45 laptop (new CI lane for njeremoto-operations) failed twice in a row after the agent itself installed fine:

1. `config.sh` aborted with "No usable version of libssl was found". The runner's .NET runtime only loads OpenSSL 1.1/3, but Fedora 45 ships OpenSSL 4 (`libssl.so.4`) and has retired `compat-openssl11`.
2. The systemd runner services then died at `status=203/EXEC` (`runsvc.sh: Permission denied`) with SELinux Enforcing — and the denial is `dontaudit`'d, so `ausearch` shows nothing, which makes it look like a filesystem-permission problem. It is not.
3. A third latent one: relabeling the whole runner tree `bin_t` to fix (2) broke container jobs later with `EACCES` on `/__w/_temp/_runner_file_commands/...` — `container_t` may only write `container_file_t`, and the host-side runner runs as `unconfined_service_t` so the breakage only shows up inside jobs.

## What we decided

Self-hosted Actions runners on modern Fedora get three setup steps, applied together: `openssl3-libs` installed; runner *code* labeled `bin_t` and the `_work` *area* labeled `container_file_t` (both via `semanage fcontext` + `restorecon`, not ad-hoc `chcon`); and when an exec/write denial looks like plain permissions but nothing is in the audit log, suspect a `dontaudit`'d SELinux rule first.

## Why

The three failures are ordered and non-obvious: the libssl one is documented for RHEL (where `compat-openssl11` exists) but the package is gone on Fedora 45, and `openssl3-libs` is the working replacement. The SELinux pair is invisible without prior knowledge: 203/EXEC with an empty audit log reads as a broken script, and the container EACCES reads as a uid mismatch (the container user *is* uid 1000 matching the host) — both waste a full debug cycle. Labeling code and work area differently is not optional; one recursive label cannot satisfy both systemd's exec requirement and container write access.

## The cost

Two extra `semanage fcontext` rules per runner directory must be re-applied whenever a runner dir is recreated or moved — easy to forget months later, and the failure mode (a service that won't start) does not point back at labels. `container_file_t` on the work area also means any container on the machine can write job workspaces; acceptable for a dedicated CI host, but it is not a general-purpose security boundary. And `dontaudit` means future denials of this class will be silent again — the runbook workaround is knowing to suspect it, not seeing it.
