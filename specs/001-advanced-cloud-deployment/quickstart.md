# Quickstart: Advanced Cloud Deployment

**Feature**: 001-advanced-cloud-deployment
**Date**: 2026-02-07

## Prerequisites

- Docker Desktop installed and running
- Minikube installed (`minikube version` >= v1.32)
- Helm installed (`helm version` >= v3.14)
- Dapr CLI installed (`dapr --version` >= 1.13)
- kubectl installed
- Node.js 20+ and pnpm (frontend)
- Python 3.13+ and uv (backend)
- Neon DB account with existing database from Phase 3-4
- GitHub account (for CI/CD)

## Local Development (docker-compose)

```bash
# 1. Clone and enter the project
cd phase-5-advanced-cloud-deployment

# 2. Copy environment variables
cp .env.example .env
# Fill in: DATABASE_URL, BETTER_AUTH_SECRET, OPENAI_API_KEY

# 3. Run database migrations
cd backend && uv run alembic upgrade head && cd ..

# 4. Start all services
docker-compose up --build
```

Frontend: http://localhost:3000
Backend: http://localhost:8000
Backend docs: http://localhost:8000/docs

## Minikube Deployment

```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=4

# 2. Install Dapr
dapr init -k --wait

# 3. Install Redpanda (Kafka-compatible)
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda \
  --namespace redpanda --create-namespace \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=1Gi \
  --set tls.enabled=false \
  --set external.enabled=false

# 4. Create Kubernetes secrets
kubectl create secret generic db-credentials \
  --from-literal=connection-string="$DATABASE_URL"
kubectl create secret generic app-secrets \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --from-literal=openai-api-key="$OPENAI_API_KEY"

# 5. Deploy Dapr components
kubectl apply -f dapr-components/

# 6. Build and load images into Minikube
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend

# 7. Deploy with Helm
helm install todo-app ./helm/todo-app

# 8. Access the application
minikube tunnel
# Frontend: http://localhost (via LoadBalancer)

# 9. Verify
kubectl get pods
dapr status -k
```

## Cloud Deployment (AKS/GKE/OKE)

```bash
# 1. Connect kubectl to cloud cluster
# (provider-specific: az aks get-credentials / gcloud container
# clusters get-credentials / oci ce cluster create-kubeconfig)

# 2. Install Dapr on cloud cluster
dapr init -k --wait

# 3. Install Strimzi Kafka operator
kubectl create namespace kafka
kubectl apply -f \
  'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f helm/kafka-cluster.yaml

# 4. Create secrets (same as Minikube step 4)

# 5. Deploy Dapr components
kubectl apply -f dapr-components/

# 6. Deploy with Helm (cloud values)
helm install todo-app ./helm/todo-app \
  -f helm/todo-app/values-cloud.yaml

# 7. Get external IP
kubectl get svc todo-frontend -o wide
```

## Verification Checklist

- [ ] All pods are Running: `kubectl get pods`
- [ ] Dapr sidecars injected: `kubectl get pods -o jsonpath='{.items[*].spec.containers[*].name}'`
- [ ] Health checks pass: `curl http://<backend>/health`
- [ ] Create a task via UI and verify Kafka event:
      `kubectl exec -it redpanda-0 -n redpanda -- rpk topic consume task-events --num 1`
- [ ] Chatbot responds to "Add a high priority task"
- [ ] Reminder fires at scheduled time
- [ ] Recurring task creates next occurrence on completion

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Pod not starting | `kubectl describe pod <name>` |
| Dapr sidecar missing | Verify annotation `dapr.io/enabled: "true"` |
| Kafka connection refused | `kubectl get pods -n redpanda` |
| Events not flowing | `dapr logs -k -a backend-service` |
| DB connection error | Verify secret: `kubectl get secret db-credentials -o yaml` |
