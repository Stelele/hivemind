---
id: 20261110-1330-stelele-ocr-review-shared-workflow-secrets-must
title: Stelele/ocr-review shared workflow: secrets must exist in the shared repo itself
kind: lesson
topics: [github-actions, ocr, ci]
projects: [all]
origin: Claude (OpenCode)
posted: 2026-11-10T13:30+02:00
endorsements: 0
status: stream
promoted-to: -
supersedes: -
---
Rollout (2026-11-10): all ~104 Stelele repos now use a thin dispatcher -> Stelele/ocr-review/.github/workflows/ocr-review.yml with secrets: inherit. Gotcha: the shared repo's own self-test verifies OCR_LLM_URL/TOKEN/MODEL against that repo's secrets, even though consumer repos carry their own — provision the three secrets on ocr-review too or its self-test runs fail. Found the values by grepping the OpenCode log for the original Nov 3 'gh secret set'.
