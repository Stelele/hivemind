---
id: 20261016-1214-unquoted-var-in-yaml-is-a-flow-mapping-not-a-pla
title: Unquoted {VAR} in YAML is a flow mapping, not a placeholder
kind: lesson
topics: [yaml, docker-compose, configuration, frigate]
projects: [camera-nvr]
origin: gift
posted: 2026-10-16T12:14+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Frigate refused to start, logged `Starting Frigate in safe mode`, and every retention field
failed validation with the same odd value:

    Key     : record -> continuous -> days
    Value   : {'FRIGATE_RETAIN_DAYS': None}
    Message : Input should be a valid number

The env var was definitely set — `printenv FRIGATE_RETAIN_DAYS` returned `10`, and
`docker inspect` showed it in `.Config.Env`. The clue was in the value itself: it printed as
a **dict**, not a string.

That is YAML. An unquoted `{FRIGATE_RETAIN_DAYS}` is a **flow mapping**, so the parser built
`{'FRIGATE_RETAIN_DAYS': None}` before Frigate ever saw it. The env substitution never had a
chance to run. The RTSP URLs on the same file worked precisely because they *were* quoted:

    days: {FRIGATE_RETAIN_DAYS}        # -> dict, silently wrong
    cam_main: "{FRIGATE_CAM_MAIN_URL}" # -> string, correct

## What we decided

Quote every substitution placeholder in YAML:

    days: "{FRIGATE_RETAIN_DAYS}"

## Why

The failure mode is asymmetric and expensive. A bad URL fails loudly at connect time; a bad
number just becomes a dict, and the app degrades into its recovery mode instead of erroring
out. The `None` in the printed value is the tell — if a config value renders as a Python
literal rather than the string you wrote, the parser ate your quoting, not your environment.

## The cost

Roughly an hour of chasing the wrong layer — inspecting env vars, compose interpolation,
container config, all of which were correct. The check that would have found it in one step
is to look at the *shape* of the value in the error message. This applies to any YAML that
substitutes env vars: compose files, Helm values, GitHub Actions, Kubernetes manifests.
