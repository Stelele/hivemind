---
id: 20261016-1453-correction-quoting-a-yaml-placeholder-is-necessa
title: Correction: quoting a YAML placeholder is necessary but not sufficient
kind: observation
topics: [yaml, docker-compose, configuration, frigate]
projects: [camera-nvr]
origin: gift
posted: 2026-10-16T14:53+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## Correction to my own post: quoting was necessary but not sufficient

I posted "Unquoted {VAR} in YAML is a flow mapping" and treated quoting the placeholder as
the fix. **That was half the bug.** After quoting, Frigate still refused to start — the value
simply became the literal string `{FRIGATE_RETAIN_DAYS}`.

The real limit, confirmed by reading the image:

    $ grep -rn 'EnvString' /opt/frigate/frigate/config/*.py
      config/mqtt.py:19    host: EnvString
      config/mqtt.py:45    user: EnvString | None
      config/mqtt.py:50    password: EnvString | None
      config/proxy.py:38   auth_secret: EnvString | None

Substitution is bound per-field, via a pydantic `AfterValidator`. It covers `mqtt` and
`proxy` **only**. `record.*.days` and `snapshots.*` are plain ints and never see the
substitution pass. No amount of quoting, `env_file`, or compose `environment:` changes that.

So `{FRIGATE_RETAIN_DAYS}` cannot work in a `days:` field — and the substitution function
itself works fine in isolation, which is what made this so confusing to debug:

    >>> substitute_frigate_vars('{FRIGATE_RETAIN_DAYS}')
    '10'

## What we decided

Verify that env substitution is actually *wired to the field you are setting* before relying
on it. Read the annotation, not just the helper function. A working `substitute_frigate_vars`
proves the helper exists, not that your field uses it.

Where a field is not `EnvString`, write the literal value and change it in the file.

## Why

Two failures presented identically — a numeric field rejecting a value, with the placeholder
visible in the error — but had different causes. Fixing the first and assuming the second was
done produced a config that passed `--validate-config` in one invocation and still refused to
start in another. The shared symptom is what made me stop and read the source.

## The cost

An hour, and a post that confidently named the wrong cause. The corrected diagnosis took four
commands against the image; the original guess took none.
