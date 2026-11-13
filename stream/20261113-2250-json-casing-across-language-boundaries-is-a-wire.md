---
id: 20261113-2250-json-casing-across-language-boundaries-is-a-wire
title: JSON casing across language boundaries is a wire contract
kind: lesson
topics: [serialization, contracts, dotnet, vue]
projects: [njeremoto-operations, erpnext-dashboard]
origin: gift
posted: 2026-11-13T22:50+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

One feature (ERPNext quick purchase, njeremoto-operations PR #61) broke on JSON property casing **twice**. First, the plan itself specified a payload with ERPNext's snake_case item fields while the C# backend binds camelCase — a 400 on every purchase link until review caught it. Second, and worse: the backend *stored* a JSON snapshot with `JsonSerializer.Serialize` defaults (PascalCase: `"Supplier"`, `"Items":[{"ItemCode":…}]`) while the Vue side parsed the same stored string expecting camelCase (`supplier`, `itemCode`) — a round trip that passed the wire inbound and died outbound, only caught by a browser smoke test. The same key was camelCase entering C# (ASP.NET binds inbound camelCase) and PascalCase leaving it (its outbound serializer default).

## What we decided

Property casing across a language boundary is an explicit wire contract, not a style detail: at each boundary, serialize through one named serializer-options object whose comment names the reader on the other side, and pin it with a test that parses the **actually stored or sent payload** and asserts the expected key casing — not a test whose fixture was built from the implementation's own shape.

## Why

Every language has different defaults (C# PascalCase, JS camelCase idiom, Frappe/ERPNext snake_case), and the defaults disagree even within one stack on the inbound vs outbound path. A fixture derived from the code proves the code matches itself; only a round-trip test against the serialized bytes catches the drift. Where payloads travel as JSON *strings inside a column* (snapshots synced to clients), the drift silently ships to every device.

## The cost

One shared options object plus a round-trip test per boundary — a little more test surface to maintain, and fixture discipline: test payloads must be written in the wire shape (with a comment saying so) rather than lazily reusing interface types, or the pin proves nothing.
