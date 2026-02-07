---
id: 007
title: Minikube Deployment Part B
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 001-advanced-cloud-deployment
branch: master
user: Waqar
command: implement
labels: ["minikube", "helm", "dapr", "kubernetes", "deployment", "part-b"]
links:
  spec: specs/001-advanced-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - helm/todo-chatbot/templates/postgres-statefulset.yaml
  - helm/todo-chatbot/templates/backend-deployment.yaml
  - helm/todo-chatbot/templates/dapr-components.yaml
  - helm/todo-chatbot/templates/secrets.yaml
  - helm/todo-chatbot/values.yaml
  - helm/todo-chatbot/values-cloud.yaml
  - helm/todo-chatbot/values-minikube.yaml
tests:
  - backend/tests/ (38 tests passing)
  - Minikube deployment verification (health, ready, CRUD)
---

## Prompt

you should dicide yourself as per the shared docs

(User provided full hackathon documentation for Phase V with Part A/B/C breakdown. After completing Part A features, Docker Compose testing, test fixes, and PR merge, user asked agent to proceed autonomously per the hackathon docs.)

## Response snapshot

Implemented Part B: Local Minikube Deployment with full Dapr stack.

### Changes Made:
1. **PostgreSQL StatefulSet** - Added `postgres-statefulset.yaml` Helm template with persistent volume, health probes, and secret-based password
2. **Init Containers** - Backend deployment now waits for PostgreSQL and Kafka readiness before starting
3. **Dapr Components Fixed** - Added namespace templating (`{{ .Release.Namespace }}`), removed invalid `.spec.auth` field, removed non-existent `scheduler.kubernetes` component type
4. **Secrets Template Enhanced** - Auto-generates `DATABASE_URL` from PostgreSQL config when enabled, adds `POSTGRES_PASSWORD`, provides fallback defaults for dev
5. **values-minikube.yaml** - Complete Minikube-specific configuration with local images (`pullPolicy: Never`), NodePort services, debug Dapr logging
6. **values-cloud.yaml** - Added `postgresql.enabled: false` for cloud (uses Neon serverless)

### Deployment Verification:
- Minikube started with Docker driver
- Dapr v1.16.8 initialized on Kubernetes (5 components all Healthy)
- Helm chart deployed (revision 4, STATUS: deployed)
- All pods running: backend (2/2 with Dapr sidecar), frontend, PostgreSQL, Redpanda
- Health endpoint: `{"status": "healthy", "version": "phase-5"}`
- Readiness: `{"status": "ready", "checks": {"database": true, "dapr": true}}`
- Task CRUD verified: created task with all Phase 5 fields (priority, tags, recurrence)
- 38/38 backend tests passing

## Outcome

- ✅ Impact: Part B complete - full Minikube deployment with Dapr, PostgreSQL, Redpanda (Kafka), init containers, health/readiness probes
- 🧪 Tests: 38/38 passed (contract, integration, unit) + live Minikube deployment verification
- 📁 Files: 7 files modified/created in helm/ directory
- 🔁 Next prompts: Part C - Cloud deployment (AKS/GKE/OKE), CI/CD pipeline, monitoring
- 🧠 Reflection: Dapr CRD schema validation caught invalid `.spec.auth` field and non-existent `scheduler.kubernetes` component type. Init containers critical for startup ordering. Minikube memory limits required adjusting from 4GB to match Docker Desktop allocation.

## Evaluation notes (flywheel)

- Failure modes observed: Dapr `.spec.auth` field not in CRD schema; `scheduler.kubernetes` component type doesn't exist; Helm timeout on first deploy (backend init containers + Dapr sidecar injection delay); Docker Desktop memory limit blocked 4GB allocation
- Graders run and results (PASS/FAIL): PASS - all 38 tests green, live deployment verified with CRUD operation
- Prompt variant (if applicable): autonomous-proceed (user said "you should decide yourself")
- Next experiment (smallest change to try): Increase Helm deploy timeout to 8m by default for Minikube, or add --atomic flag
