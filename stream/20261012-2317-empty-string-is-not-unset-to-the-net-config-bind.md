---
id: 20261012-2317-empty-string-is-not-unset-to-the-net-config-bind
title: Empty string is not 'unset' to the .NET config binder
kind: lesson
topics: [dotnet, docker-compose, configuration]
projects: [njeremoto-operations, class-booking-system]
origin: gift
posted: 2026-10-12T23:17+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Deploying the .NET host behind docker-compose, the container crash-looped on startup:

    Unhandled exception. System.InvalidOperationException: Failed to convert configuration
    value '' at 'GitHub:AppId' to type 'System.Int64'.

The compose file passed an optional numeric setting as `${OPERATIONS_GITHUB_APP_ID:-}`,
which yields an *empty string* when unset — and `Get<T>()` cannot bind an empty string to a
non-nullable `long`.

## What we decided

In compose, default optional numeric options to the app's own "not configured" sentinel —
`${VAR:-0}` — instead of `${VAR:-}`. The operations app already treats `AppId == 0` as
unconfigured (`IsConfigured => AppId > 0`), so `:-0` binds cleanly and degrades identically.

## Why

An empty string and a missing key are not the same to the .NET config binder. A missing key
leaves the property at its CLR default (`0`); an empty string forces a parse of `''` into
`long`, which throws. This only bites non-nullable value types (`long`, `int`, `bool`);
`string` and nullable options bind an empty string without error.

## The cost

The `:-0` sentinel only works because the app already defined `0` as "off". A config object
with no not-configured sentinel needs the option widened to `long?` instead — a code change,
not a compose tweak.
