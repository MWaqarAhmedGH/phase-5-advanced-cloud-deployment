# Implementation Plan: Advanced Cloud Deployment

**Branch**: `001-advanced-cloud-deployment` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-advanced-cloud-deployment/spec.md`

## Summary

Implement advanced todo features (priorities, tags, search/filter/sort,
due dates, reminders, recurring tasks), integrate event-driven
architecture (Kafka via Dapr Pub/Sub), deploy with full Dapr runtime
(State, Secrets, Service Invocation, Jobs) on Minikube and a managed
cloud Kubernetes service, and set up CI/CD via GitHub Actions.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Node.js 20+ (frontend)
**Primary Dependencies**: FastAPI, SQLModel, OpenAI Agents SDK, Official MCP SDK, Dapr SDK (HTTP), Next.js, OpenAI ChatKit
**Storage**: Neon Serverless PostgreSQL (primary), Dapr State Store (conversation cache), Kafka (events)
**Testing**: pytest (backend), vitest or jest (frontend), helm test (K8s)
**Target Platform**: Kubernetes (Minikube local, AKS/GKE/OKE cloud)
**Project Type**: Web application (frontend + backend + infrastructure)
**Performance Goals**: <2s search response, <30s reminder accuracy, <60s recurring task spawn
**Constraints**: All infra interactions via Dapr HTTP API, no direct Kafka client libraries, no hardcoded secrets
**Scale/Scope**: Single-user to small team usage, up to 1000 tasks per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | All code generated from this plan via Claude Code |
| II. Event-Driven Architecture | PASS | Kafka via Dapr Pub/Sub for all task events |
| III. Dapr Abstraction Layer | PASS | All 5 Dapr building blocks used (Pub/Sub, State, Service Invocation, Secrets, Jobs) |
| IV. Cloud-Native Portability | PASS | Helm charts, same YAML on Minikube and cloud |
| V. Test-First (TDD) | PASS | Contract tests for API, integration tests for events |
| VI. Observability | PASS | Health endpoints, structured logging, Dapr tracing |
| VII. Smallest Viable Diff | PASS | Additive changes only, Phase 1-4 preserved |

**GATE RESULT: ALL PASS** -- proceeding to design.

## Project Structure

### Documentation (this feature)

```text
specs/001-advanced-cloud-deployment/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 research findings
├── data-model.md        # Entity definitions and migrations
├── quickstart.md        # Setup and deployment guide
├── contracts/
│   ├── rest-api.md      # Extended API contracts
│   └── dapr-components.md # Dapr component YAML contracts
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py              # FastAPI entry point + Dapr subscription
│   ├── models/
│   │   ├── task.py          # Extended Task model (priority, tags, etc.)
│   │   ├── task_tag.py      # TaskTag model
│   │   ├── conversation.py  # Existing
│   │   └── message.py       # Existing
│   ├── routes/
│   │   ├── tasks.py         # Extended CRUD with search/filter/sort
│   │   ├── chat.py          # Existing chat endpoint
│   │   ├── events.py        # Dapr event subscription handlers
│   │   ├── jobs.py          # Dapr Jobs callback handler
│   │   └── health.py        # Health and readiness endpoints
│   ├── services/
│   │   ├── event_publisher.py   # Dapr Pub/Sub publish helper
│   │   ├── reminder_service.py  # Dapr Jobs scheduling
│   │   ├── recurring_service.py # Recurring task processor
│   │   └── notification_service.py # SSE push for reminders
│   ├── mcp/
│   │   ├── server.py        # Extended MCP tools
│   │   └── tools.py         # add_task, list_tasks (with new params)
│   ├── db.py                # Database connection (existing)
│   └── auth.py              # JWT verification (existing)
├── migrations/
│   └── versions/            # Alembic migration for new columns/tables
├── tests/
│   ├── contract/
│   │   └── test_api.py      # API contract tests
│   ├── integration/
│   │   └── test_events.py   # Event publish/consume tests
│   └── unit/
│       ├── test_search.py   # Search/filter/sort logic
│       └── test_recurring.py # Recurring task logic
├── Dockerfile               # Multi-stage build
├── pyproject.toml
└── .env.example

frontend/
├── app/
│   ├── (pages)/
│   │   ├── page.tsx         # Task list with filters/sort
│   │   └── chat/page.tsx    # Chatbot (existing)
│   ├── components/
│   │   ├── TaskCard.tsx     # Extended with priority badge, tags, due date
│   │   ├── TaskFilters.tsx  # Search bar, priority/status/tag filters
│   │   ├── TaskSort.tsx     # Sort dropdown
│   │   ├── TaskForm.tsx     # Extended with priority, tags, due date, recurrence
│   │   ├── ReminderBanner.tsx  # In-app reminder notification
│   │   └── ChatWidget.tsx   # Existing chatbot component
│   ├── lib/
│   │   ├── api.ts           # Extended API client
│   │   ├── notifications.ts # Browser Notification API wrapper
│   │   └── sse.ts           # Server-Sent Events client for reminders
│   └── layout.tsx
├── Dockerfile               # Multi-stage build
├── package.json
└── .env.example

helm/
├── todo-app/
│   ├── Chart.yaml
│   ├── values.yaml          # Local defaults
│   ├── values-cloud.yaml    # Cloud overrides
│   └── templates/
│       ├── backend-deployment.yaml   # With Dapr annotations
│       ├── frontend-deployment.yaml  # With Dapr annotations
│       ├── backend-service.yaml
│       ├── frontend-service.yaml
│       ├── ingress.yaml              # Cloud ingress
│       └── _helpers.tpl
├── kafka-cluster.yaml       # Strimzi Kafka CR (cloud)
└── redpanda-values.yaml     # Redpanda Helm overrides (local)

dapr-components/
├── kafka-pubsub.yaml        # Pub/Sub component
├── statestore.yaml          # PostgreSQL state store
└── kubernetes-secrets.yaml  # Secret store

.github/
└── workflows/
    └── ci-cd.yaml           # Build, test, deploy pipeline

docker-compose.yml           # Local dev orchestration
.env.example                 # Environment variable template
```

**Structure Decision**: Web application structure (Option 2) with
additional infrastructure directories (helm/, dapr-components/,
.github/). Extends Phase 4 structure with Dapr components and CI/CD.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dapr sidecar adds per-pod overhead | Required by constitution Principle III for infrastructure abstraction | Direct Kafka/DB access would couple code to specific backends |
| 5 Dapr building blocks | Hackathon explicitly requires Pub/Sub, State, Secrets, Service Invocation, Jobs | Using fewer would not meet Phase 5 requirements |
| Strimzi + Redpanda (two Kafka options) | Redpanda for fast local dev, Strimzi for cloud learning experience | Single option would compromise either local DX or cloud learning |

## Architecture Decisions

### AD-1: Dapr as the Integration Layer

All infrastructure interactions go through Dapr sidecar HTTP API at
`http://localhost:3500`. The application code never imports kafka-python,
redis, or direct cloud SDKs.

**Rationale**: Constitution Principle III. Swapping backends (Kafka to
RabbitMQ, PostgreSQL to Redis for state) requires only YAML changes.

### AD-2: Event-First for Advanced Features

Reminders and recurring tasks are implemented as event consumers, not
synchronous API logic.

- Task completion → publishes event → recurring-task consumer creates
  next occurrence.
- Reminder scheduling → Dapr Jobs API → callback fires → publishes
  event → notification service sends to client.

**Rationale**: Constitution Principle II. Decoupled services scale
independently.

### AD-3: Database Migration Strategy

New columns added to existing `tasks` table with non-breaking defaults:
- priority: default 'medium'
- recurrence: default 'none'
- due_date, reminder_offset_minutes: nullable

New `task_tags` table created.

**Rationale**: Constitution Principle VII. Backward-compatible migration
preserves Phase 3-4 functionality.

### AD-4: SSE for Reminder Delivery

Server-Sent Events (SSE) from backend to frontend for real-time
reminder notifications. Simpler than WebSockets for one-way push.
Frontend uses Browser Notification API for desktop alerts.

### AD-5: GitHub Container Registry for Images

Docker images pushed to ghcr.io (free for public repos). CI/CD pipeline
uses GitHub Actions with `docker/build-push-action`.

### AD-6: Helm Values for Environment Portability

- `values.yaml`: Local Minikube defaults (hostPath storage, Redpanda
  brokers, NodePort services).
- `values-cloud.yaml`: Cloud overrides (cloud PV, Strimzi/Redpanda
  Cloud brokers, LoadBalancer services, ingress).

Same Helm chart, different values file. Constitution Principle IV.
