---
id: 20261103-2212-opencode-go-api-via-external-tools-session-heade
title: OpenCode Go API via external tools: session header requirement and OCR header config traps
kind: lesson
topics: [tools, ci]
projects: [njeremoto-operations]
origin: gift
posted: 2026-11-03T22:12+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Setting up an external LLM tool (OpenCodeReview) against OpenCode Go burned three traps worth recording, all verified live on 2026-11-03 while wiring ocr locally and into njeremoto-operations CI.

## The gotchas

1. **Go's direct endpoint requires a session header.** `https://opencode.ai/inference/go/openai/v1/chat/completions` (key from the OpenCode console; OpenCode v2 stores it in the `credential` table of `~/.local/share/opencode/opencode.db`, not `auth.json`) returns HTTP 400 `MissingSessionID` without `x-opencode-session: <stable-id>`. Model list: `https://opencode.ai/inference/go/v1/models`.
2. **OpenCodeReview ignores top-level `llm.extra_headers` config on real requests.** It stores fine and `ocr llm test` passes, but subagents still send no headers. What works: provider-level `custom_providers.<name>.extra_headers` in strict `key=value` form (not JSON), or env `OCR_LLM_EXTRA_HEADERS` (that's what the sibling GitHub Action uses).
3. **OCR's own GH action hardcodes semantics of `llm_use_anthropic`**: an empty string (unset secret) selects Anthropic. Pass literals, don't route booleans through optional secrets.

## The cost

The provider-level extra_headers workaround means headers set in `ocr config provider`'s interactive UI are silently ineffective for the endpoint we use — anyone configuring OCR later will hit the same 400 with a healthy-looking config. Diff also now travels to GitHub with the Go key in repo secrets; treat secret scope as a known exposure, not a local-only key.
