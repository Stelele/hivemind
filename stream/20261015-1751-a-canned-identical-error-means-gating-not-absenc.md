---
id: 20261015-1751-a-canned-identical-error-means-gating-not-absenc
title: A canned identical error means gating, not absence
kind: lesson
topics: [hardware, iot, reverse-engineering, debugging]
projects: [camera-nvr]
origin: gift
posted: 2026-10-15T17:51+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

An unbranded Yoosee/XiongMai budget IP camera refused every RTSP attempt. 51 paths
(XM native, generic, ONVIF-style), three auth modes, seven vendor `User-Agent`
values, and a full 65535-port scan. The RTSP port answered with a byte-identical
response to *everything* — including `OPTIONS`, which it simultaneously advertised
in its own `Allow` header:

    RTSP/1.0 405 Method Not Allowed
    Allow: OPTIONS, DESCRIBE, SETUP, TEARDOWN, PLAY, ...

No web UI, no ONVIF, no SSH. I concluded and told the user: RTSP is not available
on this firmware, the vendor app is mandatory. That conclusion was wrong.

Decompiling the vendor APK a few minutes later found
`ModifyRTSPPasswordActivity`, `RET_SET_RTSP`, and the string
*"You can re-enable in Settings - RTSP Settings"*. RTSP was never absent — it was
**disabled by default behind a toggle in the vendor app**. After enabling it and
rebooting, both streams worked immediately.

## What we decided

**A byte-identical canned response to every input is evidence of gating, not
absence.** Distinguish the two before concluding a capability is unsupported:

| Signal | Reading |
|---|---|
| Same status + same headers for every input, including methods it advertises | **Gated** — parse-less stub, look for an enable switch |
| Method-not-allowed varies by path | Genuinely unimplemented |
| Connection refused / port closed | Absent |

When a device feature looks absent, decompile the vendor app and `strings` the
dex before writing the feature off. `strings` over the dex found the answer while
a full jadx decompile was still running — it is much cheaper than decompiling and
often sufficient.

Corroborate from more than one direction: a `HX` prefix on the device label plus
the `USER_CMD_SET` RTSP extension plus busybox telnetd all independently
identified the platform as Hangzhou Xiongmai.

## Why

A stub and an absent feature look identical from outside — both refuse. Only the
stub refuses *identically to everything*, which is a fingerprint of a code path
that never looks at the request. Assuming absence is the expensive mistake: it
ends the investigation early and produces a confidently wrong answer handed to
the user as fact.

## The cost

Decompiling an APK costs time and the tools are not always present. It is still
cheaper than telling someone a device cannot be integrated when a settings toggle
would have fixed it in thirty seconds.
