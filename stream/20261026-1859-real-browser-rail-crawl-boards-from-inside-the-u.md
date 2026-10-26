---
id: 20261026-1859-real-browser-rail-crawl-boards-from-inside-the-u
title: Real-browser rail: crawl boards from inside the user's own Chrome (CDP/Xvfb), never against the wall
kind: lesson
topics: [crawler, anti-bot, playwright, consent]
projects: [remote-first-corpus, corpus-pipelines]
origin: gift
posted: 2026-10-26T18:59+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
# Real-browser rail: crawl boards from inside the user's own Chrome (CDP/Xvfb), never against the wall

## What I hit

Mid-session build of a tech-corpus (Bayt.com, GulfTalent) hit Rails that
flatly refuse automated access: Cloudflare Turnstile ("Just a moment…") and
Akamai (403 `cpt1::…` receipts) — under plain requests, headless Chromium,
and Firefox/Playwright on a datacenter IP alike. Meanwhile, one unrelated
job board (Jobberman) loaded without friction inside the user's own desktop
Chrome. Two insights stacked: the browser that *didn't* get challenged was
the one real session, i.e. a human-context one; and on a session where the
user's cookies are present, the challenge often deletes itself.

Separately — a recurring operational trap: "attach to the user's Chrome"
was easy to suggest but hard to *do* because Chrome 155+ kernel-seals
`/proc/<pid>/environ` (all zeros), so lifting `DISPLAY`/`XAUTHORITY` to
relaunch in the user's session is impossible; modern desktops (KDE Wayland +
Xwayland) hide the X11 auth cookie not in `~/.Xauthority` but in
`/run/user/<uid>/xauth_XXXX` next to the Xwayland process — hence the failed
first relaunch ("Authorization required, but no authorization protocol
specified") and the correct one after reading pgrep for `-auth`.

## What we decided

When a board hard-blocks us: **do not evade**. Attach to, and drive, a
*real session the user consents to* — their live Chrome over CDP
(`--remote-debugging-port=9222`, ideally with a scoped
`--user-data-dir=/tmp/chrome-bot`), or a real (non-headless-fake) Chromium
under Xvfb when no display exists. Full recipe encoded as a reusable skill:

```
~/.config/opencode/skills/real-browser-rail/SKILL.md
```

It covers relaunch diagnostics (the environ-seal dead end, the Xwayland
xauth discovery, SingletonLock cleanup, the sitemap/robot-restricted-page
paths), the Playwright `connect_over_cdp` attach/behaviour rules
(one-page-per-context for warm `cf_bm` cookies, never reuse cookie-free
new_tabs, 1.5–4 s politeness per page load, storage_state rescues), the
jobs→companies inversion pattern for job-board crawls, and a signed line
that when the rail refuses a *real* browser too, the answer is a
console-snippet handoff to the user (human in the DevTools console on
their own logged-in view) — never a fingerprinting fight.

## Why

1. **Consent replaces evasion.** Inside a session the user owns, there is
   no "bot" to fool — Turnstile's same-origin kringle clears itself. This
   also stays on the honest side of ToS: we are *using the site as a
   human*, with the user's explicit permission, no account spoofing, no
   solver plugins, no fingerprint mutations.
2. **It's cheap and reusable.** Every rail that 403s can be re-scored in
   this order: (a) plain crawl fail → (b) Xvfb real-Chromium auto-pass →
   (c) user-session CDP → (d) user console-snippet handoff. That decision
   tree now lives in the skill, and the "how to get Xwayland auth" part is
   the piece I would have lost without writing it down.
3. **The privacy trade is a subject-level decision, not ours.** CDP attach
   exposes every tab in the attached profile; we always offer the scoped
   `--user-data-dir` alternative and this consideration is now hard-coded
   as step 0 of the skill.

## The cost

1. **The user's screen is shared workbench.** Driving their Chrome means
   their visible window flickers, and it needs negotiating before every
   sweep (what pages, how long). That's overhead at the start of each rail.
2. **Politeness limit.** Even permitted, the rate is human-ish (seconds per
   action); a "drive-my-chrome" sweep solves unlocks and directories, not
   bulk harvests. Big-volume needs still route through public APIs/SSR
   endpoints.
3. **Turnstile isn't always auto-clearing.** Even inside a real session a
   challenge can persist (Bayt later did on subsequent tabs). When a user's
   session still hits the wall, the remaining moves are wider-consent work
   (phone, one-time login by user) — not code on our side. The skill keeps
   that ceiling explicit so nobody burns an evening tuning fingerprints.
