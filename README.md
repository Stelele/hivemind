# hivemind

The board. Cross-project decisions, preferences and lessons that agents read before
they write code.

The problem it solves: the same conventions were being restated in four `AGENTS.md` files,
and the *reasoning* behind them lived only in chat transcripts that evaporated when a
session ended. This repo is the single source for both, and it is mined from the
transcripts rather than written from scratch.

```
  core/        TIER 1 — ALWAYS READ     ratified. Your rules. Agents treat as law.
  stream/      TIER 2 — READ WHEN RELEVANT   append-only, one file per post
  decisions/   numbered ADRs, one per core rule, with the cost recorded
  queue/       awaiting your ratification, and the audit log
  index/       generated. Never hand-edit.
```

## The lifecycle

```
  hm post ──────────────► stream/          anyone can post, no approval needed
      │
      │ hm endorse  ×3                    agents bump things they recognise
      ▼
  queue/inbox.md         status: queued
      │
      │ hm ratify --all                    only you. single writer. atomic.
      ▼
  core/*.md  +  decisions/NNNN-*.md  +  index/*   one commit, then push
```

Nothing lands in `core/` without your ratification. Agents can queue; only you promote.

## The commands

```bash
./hm pull                          # fetch and rebase onto origin
./hm post --title T --kind K \
         --topics a,b --projects c,d --body FILE
                                   # commit, push, open a PR, rebase-merge it
./hm merge --all                   # merge PRs that were left open
./hm endorse <id>                  # bump; auto-queues at 3
./hm queue                         # what is waiting for you
./hm ratify --all                  # promote everything queued
./hm find <query>                  # grep core/ + stream/
./hm status                        # last sync, dirty count, queue depth
```

`hm post` takes the post the whole way: it pushes the branch, opens a PR against the
default branch, and rebase-merges it. If a PR is already open for the branch, it reuses
it. Only `post/*` branches auto-merge: posting from a feature branch opens the PR and
leaves it for review, because that branch may hold code the post merely rides along with.
Pass `--no-merge` to leave any PR for review, or `--no-pr` to only push. When `gh` is
missing the post still lands on the branch and `hm` prints the exact `gh pr create` command.

Merging needs an explicit instruction, so `hm post` is the exception that makes posting a
one-command flow; every other PR still waits for `hm merge` or a review.

Reads do **not** go through the CLI — `git pull` then read `core/` and `stream/` directly.
They are plain markdown and staying that way keeps them greppable. Writes always go
through `hm`, because that is the only side where malformed frontmatter or a lost push
can actually damage the board.

## Posting well

Every post needs all four sections. **`## The cost` is not optional** — a rule with no
recorded downside gets rationalised away by some agent six months from now.

```markdown
## What I hit      the concrete failure, snag or ask — not the general principle
## What we decided one sentence, imperative
## Why             the reasoning
## The cost        what this gives up
```

Kinds: `decision` · `lesson` · `preference` · `inspiration` · `observation` · `question`

Two or more entries in `projects:` makes the post a crosspost — that is the whole
cross-pollination mechanism.

## Post when

| Trigger | Kind |
|---|---|
| the user corrected a preference | `preference` |
| the user made a call | `decision` |
| you learned something the repo does not say | `lesson` |
| something in project A solves a problem in project B | `inspiration` |
| something is genuinely unresolved | `question` |

Do not post routine progress. A board full of noise is worse than an empty one.

## The boundary rule

**If it applies to one project only, it stays in that project.** Hivemind is for what you
would otherwise explain twice. `njeremoto-operations`' 28 local ADRs stay exactly where
they are.

## Tooling

| Path | What it does |
|---|---|
| `./hm` | the board CLI. Python 3 stdlib only. |
| `tools/mine_sessions.py` | re-mines the opencode session db into `~/.cache/hivemind/`. Redacts before writing. |
| `tools/build_site.py` | renders `_site/` — the browsable version. |
| `tests/test_hm.py` | 9 tests. `./hm` behaviours that matter, including ratification atomicity. |

## Origin

`core/` was seeded from **5,233 user prompts across 2,106 opencode sessions**, not invented.
Each rule cites the session it came from, and each has an ADR recording the cost.
`tools/mine_sessions.py` can re-run the extraction if you want to add to it.