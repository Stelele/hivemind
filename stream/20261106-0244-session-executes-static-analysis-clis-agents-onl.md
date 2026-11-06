---
id: 20261106-0244-session-executes-static-analysis-clis-agents-onl
title: Session executes static-analysis CLIs; agents only interpret the results (analyze-codebase)
kind: preference
topics: [tooling, agents, cost, code-analysis]
projects: [all]
origin: GLM agent (njeremoto-operations session)
posted: 2026-11-06T02:44+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## Context

Designing `/analyze-codebase` (opencode skill + command around the `code-analysis` stack:
Code Maat + CodeCharta). Initial drafts let agents be thorough about *everything*, including
running the tools.

## Decision

**Execution and interpretation are separated. The session executes; agents interpret.**

- Running static-analysis CLIs (`code-analysis`, `code-analysis-setup`, `code-analysis-doctor`)
  is plain shell work — the active session does it directly, in background. SUBAGENT DISPATCH
  IS NOT USED to run tools, install them, or babysit runs.
- Delegation begins at the produced files: a lightweight agent may be given only the results
  directory (csv paths + `ccsh inspect` of the map) to interpret findings. Inputs are files,
  never repo source context.
- Model attention is for the *interpretation* (what it means, what needs improving), not for
  babysitting CLIs.

## Why

User correction during the skill design: "I don't really want heavy agents working on the
tools. I want you to run the static analysis tools then the agents read the output and
interpret what it means."

## Cost

- A single miswired wrapper hides the division: if a tool needs more than a one-line shell
  invocation, the pressure to delegate the running creeps back. Keep wrappers one-shot.
- Interpreting agents see only outputs; they miss code-context nuance. Verdicts aimed at
  changes should be drafted with a quick source look by the session, not baked into the
  agent's readout.
