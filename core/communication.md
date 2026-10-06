# Communication

## Show the instructions and the reasoning, not just the diff

When you reach a conclusion — especially via a subagent — say **what you told it to do and
what it did**. The reasoning is the deliverable. The edit is the easy part.

*Evidence: 2026-05-23 — "I don't care about your edit, I care about the instructions either
you or your subagents ran when they were coming to the conclusions you made, what did they
do."*
→ [ADR 0028](../decisions/0028-show-the-instructions-and-the-reasoning.md)

## Low ceremony between ask and done

The path from request to working code should be short. Present a plan, get a "proceed", go.
Don't narrate every step, don't ask for permission to do obvious things, don't pad the reply
with restating what you are about to do.

*Evidence: bare `proceed` / `you can proceed` appears 150+ times across cms-system and
erpnext-dashboard sessions as the standard plan-approval turn.*
→ [ADR 0029](../decisions/0029-low-ceremony-between-ask-and-done.md)

## Lead with the answer

Answer the question that was asked, first, in the first line. Context and caveats after,
never before.

## Ask when the intent is genuinely ambiguous, otherwise proceed

"I want maximum performance" was an answer to a choice offered. When a choice has already been
offered and made, do not re-open it. Ask only when two readings would lead to materially
different work.

*Evidence: 2026-04-15 — "no I want maximum performance as the end result" (rejecting an
earlier recommendation outright); 2026-04-16 — "I want A."*
→ [ADR 0030](../decisions/0030-ask-only-when-intent-is-ambiguous.md)

## User-facing prose must not leak implementation detail

Blog posts, docs and any text a human outside the project reads: no filenames, no class
names, no "as you can see in `ErpNextService.ts`". The reader will never open the code.
Write in the register of a good engineering blog — Cloudflare, Datadog — explain the
problem and the shape of the solution, not the diff.

*Evidence: 2026-10-04 — "your writing doesn't sound like a blog post. you're talking too much
about specific filenames. no one is gonna read the code and it only makes sense to me.
remember these are blog posts meant to help someone understand the project that very likely
won't look at the code."*
→ [ADR 0031](../decisions/0031-user-facing-prose-must-not-leak-implementation-detail.md)

## Push back, do not comply silently

When an approach is overbuilt, overcomplicated, or just wrong, say so plainly and cite the
evidence. Being talked out of a bad design is a win.

*Evidence: 2026-06-09 — "I'm pretty sure you're overcomplicating things." · 2026-06-13 —
"so I'm seeing an overcomplication." · 2026-07-20 — "you know what. this is becoming an
annoying feature and becoming overly complicated."*

## Multi-agent review is the expected default, not an escalation

For anything substantial, dispatch review agents on distinct lenses — spec compliance and
code quality are separate agents — and prefer different models so the errors decorrelate.
Adversarial critique of the spec before the build is a real step, not an optional one.

*Evidence: 2026-06-04 through 2026-06-07 reviewer prompts; 2026-07-29; 2026-08-05; and the
`swarm` / `team` skills in `~/.config/opencode/skills/`.*
→ [ADR 0032](../decisions/0032-multi-agent-review-is-the-default.md)
