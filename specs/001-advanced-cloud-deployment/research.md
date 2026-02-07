# Research: Advanced Cloud Deployment

**Feature**: 001-advanced-cloud-deployment
**Date**: 2026-02-07

## R1: Dapr Integration Patterns for FastAPI

### Decision
Use Dapr sidecar HTTP API for all infrastructure interactions. The
FastAPI backend communicates with Dapr at `http://localhost:3500`.

### Key Patterns

**Pub/Sub (publish)**:
```python
import httpx

async def publish_event(topic: str, event_type: str, data: dict):
    await httpx.post(
        f"http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}",
        json={"event_type": event_type, **data}
    )
```

**Pub/Sub (subscribe)** -- Dapr calls the app's endpoint:
```python
# Dapr discovers subscriptions via /dapr/subscribe
@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {"pubsubname": "kafka-pubsub", "topic": "task-events",
         "route": "/api/events/task"},
        {"pubsubname": "kafka-pubsub", "topic": "reminders",
         "route": "/api/events/reminder"}
    ]

@app.post("/api/events/task")
async def handle_task_event(request: Request):
    event = await request.json()
    # Process event (audit log, recurring task spawn, etc.)
    return {"status": "SUCCESS"}
```

**State Management**:
```python
# Save state
await httpx.post("http://localhost:3500/v1.0/state/statestore",
    json=[{"key": f"conv-{id}", "value": messages}])

# Get state
resp = await httpx.get(
    f"http://localhost:3500/v1.0/state/statestore/conv-{id}")
```

**Service Invocation**:
```
# Frontend calls backend via Dapr
http://localhost:3500/v1.0/invoke/backend-service/method/api/chat
```

**Jobs API (reminders)**:
```python
await httpx.post(
    f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
    json={
        "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data": {"task_id": task_id, "user_id": user_id}
    }
)
# Dapr calls back to: POST /api/jobs/trigger
```

**Secrets**:
```python
resp = await httpx.get(
    "http://localhost:3500/v1.0/secrets/kubernetes-secrets/db-password")
```

### Alternatives Considered
- Direct kafka-python / aiokafka: Rejected -- couples app to Kafka,
  violates Dapr abstraction principle.
- Direct SQLModel for state: Acceptable as fallback for primary data
  but Dapr state used for conversation caching.
- Celery for scheduled tasks: Rejected -- Dapr Jobs API is native to
  the sidecar, no extra infrastructure.

---

## R2: Kafka on Kubernetes

### Decision
**Local (Minikube)**: Deploy Redpanda via Helm chart. Single binary,
Kafka-compatible, no Zookeeper, fast startup (~2 min).

**Cloud**: Self-hosted Strimzi on the managed K8s cluster. Free, good
learning experience. Fallback: Redpanda Cloud Serverless (free tier).

### Redpanda on Minikube (Recommended for Local)

```bash
helm repo add redpanda https://charts.redpanda.com
helm install redpanda redpanda/redpanda \
  --namespace redpanda --create-namespace \
  --set statefulset.replicas=1 \
  --set resources.cpu.cores=1 \
  --set resources.memory.container.max=1Gi \
  --set storage.persistentVolume.size=2Gi \
  --set tls.enabled=false \
  --set external.enabled=false
```

Bootstrap server: `redpanda.redpanda.svc.cluster.local:9093`

### Strimzi on Cloud K8s

```bash
kubectl create namespace kafka
kubectl apply -f \
  'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Then apply Kafka CR:
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: taskflow-kafka
  namespace: kafka
spec:
  kafka:
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
```

Bootstrap server: `taskflow-kafka-kafka-bootstrap.kafka.svc:9092`

### Topics
- `task-events`: Task lifecycle events (created, updated, completed,
  deleted). 3 partitions, 1 day retention.
- `reminders`: Reminder due events. 1 partition, 1 day retention.
- `task-updates`: Real-time UI updates (future). 3 partitions.

### Dapr Pub/Sub Component for Kafka

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.redpanda.svc.cluster.local:9093"  # local
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "none"
```

### Alternatives Considered
- Bitnami Kafka Helm chart: Heavier, requires Zookeeper. Rejected.
- CloudKarafka: Free tier too limited (5 topics). Rejected.
- Confluent Cloud: $400 credits expire. Acceptable but Strimzi is free.

---

## R3: GitHub Actions CI/CD Pipeline

### Decision
Use GitHub Actions with:
- **Image Registry**: GitHub Container Registry (ghcr.io) -- free for
  public repos.
- **Deployment**: `helm upgrade --install` from the pipeline.
- **Auth**: Kubeconfig stored as a GitHub secret.

### Pipeline Structure

```yaml
name: CI/CD
on:
  push:
    branches: [main]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
      - uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ghcr.io/${{ github.repository }}/frontend:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: azure/setup-kubectl@v3
      - uses: azure/setup-helm@v3
      - run: |
          echo "${{ secrets.KUBECONFIG }}" > kubeconfig
          export KUBECONFIG=kubeconfig
          helm upgrade --install todo-app ./helm/todo-app \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --wait --timeout 5m
```

### Cluster Authentication by Provider
- **AKS**: `az aks get-credentials` or kubeconfig in secrets.
- **GKE**: `gcloud container clusters get-credentials` or service
  account JSON in secrets.
- **OKE**: OCI CLI config or kubeconfig in secrets.

### Rollback Strategy
Kubernetes rolling update with `maxUnavailable: 0` and
`maxSurge: 1`. If readiness probe fails, rollout stalls and previous
ReplicaSet stays. Pipeline uses `--wait` flag to detect failure.
Manual rollback: `helm rollback todo-app`.

### Environment-Specific Values
- `helm/todo-app/values.yaml` -- defaults (local/Minikube)
- `helm/todo-app/values-cloud.yaml` -- cloud overrides (image registry,
  resource limits, ingress, Kafka brokers)
- Pipeline uses: `helm upgrade -f values-cloud.yaml`

### Alternatives Considered
- ArgoCD / FluxCD for GitOps: Over-engineered for hackathon. Rejected.
- Docker Hub: Rate limits on free tier. ghcr.io preferred.
- Skaffold: Good for dev loop but not CI/CD. Rejected.

---

## R4: Cloud Provider Selection

### Decision
Support all three as specified in hackathon doc:
**Primary recommendation: Oracle OKE** (Always Free tier -- no credit
expiry). **Alternatives: Azure AKS** ($200/30 days), **GKE** ($300
credits).

### OKE Setup
1. Sign up at oracle.com/cloud/free
2. Create OKE cluster (Quick Create wizard)
3. Download kubeconfig via OCI CLI
4. `kubectl apply` Helm charts identical to Minikube

### Key Difference from Minikube
- Ingress: Use cloud provider load balancer (OCI Load Balancer, Azure
  LB, GKE Ingress) instead of `minikube tunnel`.
- Storage: Use cloud-native persistent volumes instead of hostPath.
- Secrets: Same Kubernetes Secrets, same Dapr component.
- Dapr: Same `dapr init -k` installation process.

### Alternatives Considered
- DigitalOcean DOKS: $200/60 days. Good but Oracle is Always Free.
- AWS EKS: No free tier for K8s control plane. Rejected.

---

## R5: Dapr Installation

### Decision
Install Dapr via CLI on both Minikube and cloud clusters.

### Steps (same for all K8s targets)
```bash
# Install Dapr CLI
# Windows:
winget install Dapr.CLI
# Linux/Mac:
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Initialize Dapr on K8s cluster
dapr init -k --wait

# Verify
dapr status -k
kubectl get pods -n dapr-system
```

### Sidecar Injection
Add annotation to pod spec in Helm templates:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend-service"
  dapr.io/app-port: "8000"
```

### Alternatives Considered
- Dapr Helm chart directly: CLI is simpler for hackathon.
- Manual sidecar injection: Annotation-based is standard.

---

## R6: Browser Notifications for Reminders

### Decision
Use the Web Notifications API (standard browser API) triggered by
Server-Sent Events (SSE) from the backend.

### Flow
1. Dapr Jobs API fires callback at scheduled time.
2. Backend publishes "reminder.due" event to reminders topic.
3. Notification service (or backend) pushes via SSE to connected
   frontend clients.
4. Frontend shows browser notification using Notification API.

### Alternatives Considered
- WebSockets: More complex setup. SSE is simpler for one-way push.
- Push API (Service Worker): Requires VAPID keys and push server.
  Over-engineered for hackathon.
- Polling: Inefficient. Rejected.
