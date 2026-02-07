---
id: 008
title: Cloud Deployment CI/CD Part C
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 001-advanced-cloud-deployment
branch: master
user: Waqar
command: implement
labels: ["cloud", "cicd", "dapr", "kafka", "helm", "github-actions", "part-c"]
links:
  spec: specs/001-advanced-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - .github/workflows/cd.yml
  - helm/todo-chatbot/templates/dapr-components.yaml
  - helm/todo-chatbot/templates/backend-deployment.yaml
  - helm/todo-chatbot/templates/frontend-deployment.yaml
  - helm/todo-chatbot/values-cloud.yaml
tests:
  - backend/tests/ (38 tests passing)
  - helm lint (minikube + cloud values)
  - helm template (cloud render verified)
  - Minikube upgrade (no regression)
---

## Prompt

(Continued from Part B session. Agent autonomously proceeded to Part C: Cloud Deployment per hackathon docs.)

## Response snapshot

Implemented Part C: Cloud Deployment infrastructure (CI/CD + Helm cloud config).

### CI/CD Pipeline Changes (cd.yml):
1. **Branch support** - CD now triggers on both `main` and `master` branches
2. **Dapr initialization** - Installs Dapr CLI and runs `dapr init -k` on cloud cluster
3. **Image pull secret** - Creates ghcr-pull-secret for pulling images from GitHub Container Registry
4. **Kafka cloud credentials** - Passes KAFKA_BROKERS, KAFKA_USERNAME, KAFKA_PASSWORD via GitHub Secrets
5. **Frontend URL** - Passes FRONTEND_URL from secrets for CORS config
6. **Timeout** - Increased from 5m to 8m for Dapr sidecar injection delay
7. **Failure diagnostics** - Added step to print pod descriptions and logs on failure

### Helm Chart Cloud Config:
1. **values-cloud.yaml** - Updated with correct ghcr.io image paths, LoadBalancer service, 2 replicas
2. **Dapr components** - Conditional cloud vs in-cluster Kafka: external uses SASL/SCRAM-SHA-256 + TLS
3. **imagePullSecrets** - Added to both backend and frontend deployments
4. **kafkaCloud** config block for Redpanda Cloud/Confluent credentials

### GitHub Secrets Required for Cloud Deployment:
- `KUBE_CONFIG` - Base64-encoded kubeconfig for cloud cluster
- `DATABASE_URL` - Neon serverless PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key
- `BETTER_AUTH_SECRET` - JWT signing secret
- `FRONTEND_URL` - Deployed frontend URL for CORS
- `KAFKA_BROKERS` - Cloud Kafka bootstrap servers
- `KAFKA_USERNAME` - SASL username
- `KAFKA_PASSWORD` - SASL password

## Outcome

- ✅ Impact: Part C CI/CD pipeline and cloud Helm config complete, ready for cloud cluster provisioning
- 🧪 Tests: 38/38 passed, Helm lint clean for both minikube and cloud values, Minikube upgrade no regression
- 📁 Files: 5 files modified
- 🔁 Next prompts: Provision cloud cluster (AKS/GKE/OKE), set GitHub secrets, trigger first cloud deployment
- 🧠 Reflection: Cloud deployment is infrastructure config only - no app code changes needed. Dapr abstraction means same app code works locally and in cloud by swapping Dapr component config.

## Evaluation notes (flywheel)

- Failure modes observed: None - all templates lint and render correctly
- Graders run and results (PASS/FAIL): PASS - helm lint, helm template, pytest 38/38, minikube upgrade
- Prompt variant (if applicable): autonomous-proceed
- Next experiment (smallest change to try): Provision actual cloud cluster and trigger CI/CD pipeline end-to-end
