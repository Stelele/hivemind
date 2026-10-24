---
id: 20261024-1629-opencode-agent-models-live-in-two-homes-opencode
title: OpenCode agent models live in two homes — opencode.json and markdown frontmatter
kind: lesson
topics: [opencode, model-routing, subagents]
projects: [model-router]
origin: opencode session (GLM-5.3-flash) on user instruction
posted: 2026-10-24T16:29+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
An OpenCode agent's model is resolved from **two independent homes**: the `agents` entries in
`opencode.json`, and YAML frontmatter in markdown agent files (`~/.config/opencode/agent/*.md`,
plus project `.opencode/agent/*.md`). Frontmatter is not in `opencode.json`, and it **overrides**
the JSON when both name the same agent.

The model-router `refresh` mode has been rewriting only `opencode.json`. So when free quota ran
out (2026-10-24) and every JSON agent was rewired to an `opencode-go/*` model, the markdown agent
`explore` kept `model: opencode/mimo-v2.6-flash-free` from its frontmatter — and the next
dispatch to `explore` ran the free model straight into the exhausted quota and died with
"Free usage limit reached". The failure presented as a billing complaint against a paid subscription
that *was* being paid for; the real bug was a routing file the router never looked at.

**Rule:** a routing change is not a routing change until it is applied to both homes, and a
dispatch failure is triaged by first reading what model each agent's own frontmatter pins —
`grep -h '^model:' ~/.config/opencode/agent/*.md` — not by reading `opencode.json`.

Applied: `explore.md` → `opencode-go/glm-5.3-flash`; model-router refresh mode now has a
markdown-frontmatter sync step (+ durable rule); `lineup.md` explore row carries the go model.