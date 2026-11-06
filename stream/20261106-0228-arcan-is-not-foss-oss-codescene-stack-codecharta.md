---
id: 20261106-0228-arcan-is-not-foss-oss-codescene-stack-codecharta
title: Arcan is not FOSS; OSS CodeScene stack = CodeCharta (+dep lens) + Code Maat, installed globally
kind: lesson
topics: [tooling, code-analysis, codescene]
projects: [all]
origin: GLM agent (njeremoto-operations session)
posted: 2026-11-06T02:28+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
## Context

Replacing CodeScene with a FOSS stack that runs locally (and later on GitHub Actions).
Answer looked like: CodeCharta (hotspots + code map) + Code Maat (churn, change coupling) + Arcan (architectural smells).

## Decision

**Arcan is not a pickable FOSS option.** The maintained Arcan (Arcan-Tech) is proprietary:
free-trial license only, issued via a web form/email, Docker trial, and its C# parser is
pinned to .NET Core 6.0.109 — risky on a .NET 10 codebase. The academic `mining-software-repositories/arcan`
is Java-bytecode-only and useless for C#.

**Architectural-smell duty moves to CodeCharta itself.** DependaCharta (MaibornWolff) was
merged into CodeCharta; `ccsh analyse` ≥2.2 emits a dependency lens with cycle/unstable-dependency
edges natively, parsers for C#, TypeScript, Vue, Java, C++, Python, Go, Rust, PHP... and
`ccsh gate` enforces `.codecharta.yml` cycle rules — which is the future CI/Action gate.

**Shape of the stack (user call): global, not per-repo.** CLI toolkit in `~/.local/bin` +
`~/.local/share/code-analysis`, zero files committed to any single repo:

- `code-analysis [repo] [--since] [--skip maat|log|ccsh] [--exclude]` — one-shot runner:
  Code Maat csvs (summary/coupling/entity-churn/authors/age over a `git2` log) + `ccsh analyse` map
- `code-analysis-doctor` — verifies: node ≥ 22.19, java ≥ 22, ccsh, jar, wrappers
- `code-analysis-setup` — npm install + jar fetch + doctor (ADR 0005 chain)
- `code-maat` — jar wrapper with headless AWT + 4g heap

Code Maat thresholds: `-n 2 -m 2 -i 10` (upstream defaults min-revs 5 / min-coupling 30
produce empty CSVs on repos whose history is months old).

## Why

The user explicitly asked for the toolkit to work across many repos, so per-repo scripts
would be wrong. `.cc.json.gz`, csv and the git log land under
`~/.local/share/code-analysis/results/<repo>/` — repos stay clean, nothing to gitignore.

## Cost

- jar/pins are vendored artifacts outside git (v1.0.4, 2023); doctor re-checks presence.
- CodeCharta visualization: web viewer (client-side, no upload) or local `codecharta-visualization` on port 9000.
