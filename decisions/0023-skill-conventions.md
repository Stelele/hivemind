# 0023. Skill conventions

**Status:** accepted
**Date:** 2026-10-06
**Affects:** ~/.config/opencode/skills

## Context
All four global skills — swarm, team, dotfiles, using-swarm — use exactly `name` plus a trigger-rich `description` and nothing else.

## Decision
Skills carry `name` plus a description enumerating concrete trigger phrases. No license, allowed-tools or metadata keys.

## Consequences
Skills are discovered reliably by trigger matching. The cost is that descriptions must be rewritten as triggers change.
