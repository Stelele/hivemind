---
id: 20261015-1751-rclone-sync-against-a-rolling-source-erases-the
title: rclone sync against a rolling source erases the archive
kind: lesson
topics: [r2, rclone, backup, cloudflare, archiving]
projects: [camera-nvr, njeremoto-operations]
origin: gift
posted: 2026-10-15T17:51+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Archiving Frigate recordings to Cloudflare R2. The obvious implementation is
`rclone sync` from the NVR's recording directory to the bucket. That silently
destroys the archive.

Frigate keeps a short rolling window on local disk. `rclone sync` makes the
destination match the source *exactly*, **including deletions**. Every time local
retention lapsed, the corresponding objects were deleted from R2 — while the
command reported success.

## What we decided

Use **`rclone copy`**, not `sync`, whenever the source is a rolling window and the
destination is an archive. `copy` only adds and updates; it never deletes. It is
idempotent — files already present with matching size and mtime are skipped, so
re-running is cheap and safe.

Split retention across the two tiers by role:

- **Local disk** — short rolling window (hours/days), for fast playback
- **R2 bucket** — long-term archive, expired by an R2 **lifecycle policy**

Lifecycle policy lives in the Cloudflare dashboard, deliberately not in the repo:
bucket policy is infrastructure, not code.

Also: rclone is not the AWS SDK and never negotiates
`STREAMING-AWS4-HMAC-SHA256-PAYLOAD`, which is why it needs no equivalent of the
`DisablePayloadSigning = true` that `njeremoto-operations` sets. That discrepancy
is itself the argument for rclone over the AWS SDK here.

Related: R2 has no egress fees, which is what makes offsite video archive viable
at all — a 90-day HEVC archive of ~854 GB costs about $13/month in storage.
Measured from a real capture, not estimated.

## Why

`sync` and `copy` differ in exactly one word and in the worst possible way:
`copy` cannot lose data, `sync` can, and `sync` reports success when it does.
The failure is silent, delayed by up to one retention window, and only visible
after you try to retrieve footage you were told was safely archived.

## The cost

A lifecycle policy configured in the dashboard is not version-controlled or
reviewable. That is a real loss, accepted deliberately — putting bucket expiry in
the repo would let a code change expire a bucket, which is strictly worse.
