---
id: 20261007-1919-address-coderabbit-comments-before-claiming-done
title: Address CodeRabbit comments before claiming done
kind: preference
topics: [git, review, coderabbit, agents]
projects: [frappe-offline, class-booking-system, cms-system, njeremoto-operations]
origin: gift
posted: 2026-10-07T19:19+02:00
endorsements: 1
status: stream
promoted-to: -
supersedes: -
---
## What I hit

Work was being declared done while review comments sat unaddressed on the PR.

## What we decided

**Address CodeRabbit's comments before claiming the work is done.**

Before declaring done:

1. Read the PR's review comments.
2. If CodeRabbit's rate limit is **not** exhausted and there are comments, address
   every one of them — fix it, or reply explaining why it does not apply.
3. If the rate limit **is** exhausted, or no comments were produced, say so explicitly
   and the rule is satisfied.
4. An unaddressed comment is not done. Not "done except for the nits".

```bash
gh pr view <n> --comments
gh pr checks <n>          # surfaces the rate-limit / no-review case
```

## Why

The review bot is the only reviewer on a solo-plus-AI repo. If its output is collected
but never read, the automation is theatre and you find out about it in production.

## The cost

Extra turns per PR, and some comments will be wrong. Disagreement is allowed — but it
has to be argued in a reply on the PR, not silently ignored.
