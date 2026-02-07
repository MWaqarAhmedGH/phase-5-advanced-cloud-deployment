# Dapr Component Contracts

**Feature**: 001-advanced-cloud-deployment
**Date**: 2026-02-07

## Component: kafka-pubsub

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.redpanda.svc.cluster.local:9093"
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "none"
```

**Cloud override** (values-cloud.yaml):
- brokers: `taskflow-kafka-kafka-bootstrap.kafka.svc:9092` (Strimzi)
  or Redpanda Cloud bootstrap URL.

---

## Component: statestore

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-credentials
        key: connection-string
```

---

## Component: kubernetes-secrets

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

---

## Dapr Annotations (Helm pod template)

### Backend

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend-service"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
```

### Frontend

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "frontend-service"
  dapr.io/app-port: "3000"
```

---

## Subscription Declaration

The backend exposes `/dapr/subscribe` returning:

```json
[
  {
    "pubsubname": "kafka-pubsub",
    "topic": "task-events",
    "route": "/api/events/task"
  },
  {
    "pubsubname": "kafka-pubsub",
    "topic": "reminders",
    "route": "/api/events/reminder"
  }
]
```
