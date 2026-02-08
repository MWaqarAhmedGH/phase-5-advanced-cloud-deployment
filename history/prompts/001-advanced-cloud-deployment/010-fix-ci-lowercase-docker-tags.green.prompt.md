---
id: 010
title: Fix CI Lowercase Docker Tags
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 001-advanced-cloud-deployment
branch: master
user: Waqar
command: implement
labels: ["ci", "docker", "ghcr", "bugfix"]
links:
  spec: specs/001-advanced-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .github/workflows/ci.yml
  - .github/workflows/cd.yml
tests:
  - backend/tests/ (38 tests passing)
  - GitHub Actions CI run 21789127511 (PASSED)
---

## Prompt

(Continuation from previous session) Fix CI pipeline failure: Docker image tags contain uppercase letters from GitHub username (MWaqarAhmedGH) causing `repository name must be lowercase` error when pushing to ghcr.io.

## Response snapshot

### Root Cause:
- `${{ github.repository }}` resolves to `MWaqarAhmedGH/phase-5-advanced-cloud-deployment`
- Docker image tags must be entirely lowercase
- Both CI and CD workflows had this in top-level `env` block

### Fix Applied:
1. Removed `BACKEND_IMAGE` and `FRONTEND_IMAGE` from workflow-level `env` blocks
2. Added "Set lowercase image names" step in both workflows using `tr '[:upper:]' '[:lower:]'`
3. Image names now computed at runtime via `$GITHUB_ENV`

### Verification:
- CI run 21789127511: backend-test (23s) + build-images (1m54s) both PASSED
- Backend and frontend images pushed to ghcr.io successfully

## Outcome

- ✅ Impact: CI pipeline fully green - images building and pushing to ghcr.io
- 🧪 Tests: 38/38 local + CI run PASSED
- 📁 Files: 2 files modified (ci.yml, cd.yml)
- 🔁 Next prompts: Phase 5 complete - cloud cluster provisioning requires user cloud account setup
- 🧠 Reflection: Common GitHub Actions pitfall - github.repository preserves case. Always lowercase for Docker tags.

## Evaluation notes (flywheel)

- Failure modes observed: Docker rejects uppercase in image repository names
- Graders run and results (PASS/FAIL): PASS - CI fully green
- Prompt variant (if applicable): continuation-fix
- Next experiment (smallest change to try): None - CI/CD pipeline complete and verified
