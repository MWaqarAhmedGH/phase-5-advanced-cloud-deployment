# Feature Specification: Advanced Cloud Deployment

**Feature Branch**: `001-advanced-cloud-deployment`
**Created**: 2026-02-07
**Status**: Draft
**Input**: Phase 5 of the Evolution of Todo Hackathon -- implement advanced
features, event-driven architecture, and deploy to production-grade cloud
Kubernetes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prioritize and Categorize Tasks (Priority: P1)

As a user, I can assign priority levels and tags to my tasks so that I can
organize and find tasks based on importance and category.

**Why this priority**: Priorities and tags are foundational data attributes
that search, filter, and sort (US2) depend on. They MUST exist first.

**Independent Test**: Create a task, assign priority "high" and tag "work",
verify both are stored and visible in the task list and via chatbot.

**Acceptance Scenarios**:

1. **Given** a user creating a task, **When** they set priority to
   "high", "medium", or "low", **Then** the task displays the priority
   level and it persists across sessions.
2. **Given** a user editing a task, **When** they add tags like "work"
   or "home", **Then** tags are stored, displayed, and can be removed.
3. **Given** a user talking to the chatbot, **When** they say "Add a
   high priority task to finish report tagged work", **Then** the
   chatbot creates the task with priority=high and tag=work.
4. **Given** a task with no priority set, **When** displayed, **Then**
   it defaults to "medium" priority.

---

### User Story 2 - Search, Filter, and Sort Tasks (Priority: P1)

As a user, I can search by keyword, filter by status/priority/date, and
sort tasks by due date, priority, or alphabetically so I can quickly find
what I need.

**Why this priority**: Core usability feature that directly impacts daily
task management efficiency. Co-priority with US1 since it depends on
priority/tag data.

**Independent Test**: Create 10+ tasks with varied priorities, tags, and
dates. Search for a keyword, filter by "high" priority, sort by due date.
Verify correct results.

**Acceptance Scenarios**:

1. **Given** tasks with various titles, **When** user searches for
   "groceries", **Then** only tasks containing "groceries" in title or
   description are returned.
2. **Given** tasks with different statuses, **When** user filters by
   "completed", **Then** only completed tasks are shown.
3. **Given** tasks with different priorities, **When** user filters by
   "high", **Then** only high-priority tasks are shown.
4. **Given** tasks with due dates, **When** user sorts by "due date",
   **Then** tasks are ordered by nearest due date first.
5. **Given** a chatbot user, **When** they say "Show my high priority
   tasks", **Then** the chatbot calls list_tasks with priority filter.
6. **Given** multiple filter criteria, **When** user combines status
   and priority filters, **Then** both filters apply simultaneously.

---

### User Story 3 - Due Dates and Time Reminders (Priority: P2)

As a user, I can set deadlines with date/time and receive reminders before
tasks are due so I never miss a deadline.

**Why this priority**: Enables time-based task management and is required
for recurring tasks (US4). Reminder delivery depends on event-driven
architecture (US5).

**Independent Test**: Create a task with due date 5 minutes from now and a
reminder at 2 minutes before. Verify reminder notification is received.

**Acceptance Scenarios**:

1. **Given** a user creating a task, **When** they set a due date and
   time, **Then** the deadline is stored and displayed.
2. **Given** a task with a due date, **When** user sets a reminder
   offset (e.g., 15 minutes before), **Then** the system schedules a
   reminder at the exact time.
3. **Given** a scheduled reminder, **When** the reminder time arrives,
   **Then** the user receives a notification (browser notification or
   in-app alert).
4. **Given** a chatbot user, **When** they say "Remind me about task 3
   at 2pm", **Then** the chatbot schedules a reminder via the
   scheduled jobs mechanism.
5. **Given** a task with a past due date, **When** displayed, **Then**
   it is visually marked as overdue.

---

### User Story 4 - Recurring Tasks (Priority: P2)

As a user, I can create tasks that automatically reschedule after
completion so I do not have to manually recreate repeating tasks.

**Why this priority**: Builds on due dates (US3). Requires event-driven
processing to auto-create the next occurrence.

**Independent Test**: Create a weekly recurring task, complete it, verify
a new task is automatically created for the next week.

**Acceptance Scenarios**:

1. **Given** a user creating a task, **When** they set recurrence to
   "daily", "weekly", or "monthly", **Then** the recurrence pattern is
   stored.
2. **Given** a recurring task marked as complete, **When** the
   completion event is processed, **Then** a new task is automatically
   created for the next occurrence with the same title, description,
   priority, and tags.
3. **Given** a chatbot user, **When** they say "Add weekly meeting
   every Monday", **Then** the chatbot creates a recurring task with
   weekly frequency.
4. **Given** a recurring task, **When** user deletes it, **Then** no
   further occurrences are created.
5. **Given** a completed recurring task, **When** the next occurrence
   is generated, **Then** the original task remains in completed state
   for history/audit purposes.

---

### User Story 5 - Event-Driven Architecture with Kafka and Dapr (Priority: P1)

As the system, all task lifecycle events are published to Kafka and
processed by independent consumer services so that the architecture is
decoupled and scalable.

**Why this priority**: Foundational infrastructure that reminders (US3),
recurring tasks (US4), and audit logging all depend on. Must be in place
before those features work.

**Independent Test**: Create a task via API, verify a "task.created" event
appears on the Kafka topic and is consumed by the audit service. Verify
Dapr Pub/Sub is the publish mechanism (not a direct Kafka client library).

**Acceptance Scenarios**:

1. **Given** a task is created, **When** the API processes it, **Then**
   a "task.created" event is published via Dapr Pub/Sub to the
   "task-events" topic.
2. **Given** a task is updated/completed/deleted, **When** the API
   processes it, **Then** the corresponding event type is published.
3. **Given** a reminder is due, **When** the scheduled job fires the
   callback, **Then** a "reminder.due" event is published to the
   "reminders" topic.
4. **Given** a recurring task is completed, **When** the recurring-task
   consumer receives the event, **Then** it creates the next occurrence.
5. **Given** any task event, **When** the audit consumer receives it,
   **Then** it logs the event with timestamp, user, and action for
   history.
6. **Given** Dapr sidecar is running, **When** any service publishes an
   event, **Then** Dapr routes it to Kafka without the service importing
   any Kafka client library.

---

### User Story 6 - Local Kubernetes Deployment with Dapr (Priority: P2)

As a developer, I can deploy the full system (frontend, backend, Kafka,
Dapr) to a local Minikube cluster so I can validate the cloud-native
architecture before deploying to production.

**Why this priority**: Validates the entire stack locally before
committing to cloud costs. Prerequisite for US7.

**Independent Test**: Run `helm install` on Minikube, verify all pods
are running, Dapr sidecars are injected, chatbot responds, events flow
through Kafka.

**Acceptance Scenarios**:

1. **Given** a clean Minikube cluster with Dapr installed, **When**
   Helm charts are applied, **Then** all services start within 5
   minutes and pass health checks.
2. **Given** Dapr components (Pub/Sub, State, Secrets) are deployed,
   **When** the backend publishes an event, **Then** it routes through
   Kafka via Dapr.
3. **Given** Dapr service invocation is configured, **When** frontend
   calls backend, **Then** the call routes through Dapr with automatic
   discovery.
4. **Given** Dapr secrets are configured, **When** a service requests
   credentials, **Then** Dapr provides them from Kubernetes Secrets.
5. **Given** the local deployment, **When** a user interacts with the
   chatbot, **Then** the full flow works (chat, agent, MCP tools, DB,
   Kafka events).

---

### User Story 7 - Cloud Kubernetes Deployment with CI/CD (Priority: P3)

As a team, the system is deployed to a managed cloud Kubernetes service
with automated CI/CD so that changes are continuously delivered to
production.

**Why this priority**: Final deployment target. Depends on all other
stories being functional.

**Independent Test**: Push a commit to main, verify GitHub Actions runs
the pipeline, deploys to cloud cluster, and the chatbot is accessible via
a public URL.

**Acceptance Scenarios**:

1. **Given** code is pushed to main branch, **When** GitHub Actions
   triggers, **Then** the pipeline builds container images, runs tests,
   and deploys to the cloud cluster.
2. **Given** Helm charts from Phase 4, **When** deployed to the cloud
   Kubernetes service, **Then** all services start and pass health
   checks.
3. **Given** Dapr is installed on the cloud cluster, **When** Dapr
   components point to Kafka (self-hosted or managed), **Then** events
   flow correctly in production.
4. **Given** the cloud deployment, **When** a user accesses the public
   URL, **Then** they can sign in, manage tasks, and use the chatbot.
5. **Given** monitoring is configured, **When** services emit logs and
   metrics, **Then** they are visible in the monitoring dashboard.
6. **Given** a deployment failure, **When** the pipeline detects it,
   **Then** it rolls back to the previous version automatically.

---

### Edge Cases

- What happens when Kafka is temporarily unavailable? Events MUST be
  retried via Dapr's built-in retry policy; no events are silently
  dropped.
- What happens when a recurring task has no due date? The system MUST
  reject recurrence without a base due date.
- What happens when a user searches with an empty query? Return all
  tasks (equivalent to no filter).
- What happens when the Dapr sidecar is not injected? Health check
  MUST fail and pod MUST not be marked as ready.
- What happens when a reminder fires for a deleted task? The reminder
  consumer MUST check if the task still exists and skip if deleted.
- What happens when a CI/CD deployment fails mid-rollout? Kubernetes
  rolling update strategy MUST preserve the previous working version.

## Requirements *(mandatory)*

### Functional Requirements

**Part A -- Advanced Features**

- **FR-001**: System MUST support task priority levels: high, medium,
  low (default: medium).
- **FR-002**: System MUST support free-form tags on tasks (e.g.,
  "work", "home", "urgent").
- **FR-003**: System MUST support keyword search across task title and
  description.
- **FR-004**: System MUST support filtering tasks by status, priority,
  tag, and date range.
- **FR-005**: System MUST support sorting tasks by due date, priority,
  creation date, and alphabetically.
- **FR-006**: System MUST support due dates with date and time
  precision.
- **FR-007**: System MUST support configurable reminders that fire at a
  user-specified time before the due date.
- **FR-008**: System MUST deliver reminder notifications (in-app or
  browser notification).
- **FR-009**: System MUST support recurring task patterns: daily,
  weekly, monthly.
- **FR-010**: System MUST auto-create the next occurrence of a
  recurring task upon completion of the current one.

**Part A -- Event-Driven Infrastructure**

- **FR-011**: System MUST publish task lifecycle events (created,
  updated, completed, deleted) to Kafka via Dapr Pub/Sub.
- **FR-012**: System MUST use Dapr State Management for conversation
  state storage.
- **FR-013**: System MUST use Dapr Service Invocation for inter-service
  communication.
- **FR-014**: System MUST use Dapr Secrets for all credential access.
- **FR-015**: System MUST use Dapr Jobs API for scheduling reminders at
  exact times.

**Part B -- Local Deployment**

- **FR-016**: System MUST deploy to Minikube with Helm charts and full
  Dapr integration.
- **FR-017**: Kafka MUST be deployed within the Minikube cluster
  (Redpanda or Strimzi).

**Part C -- Cloud Deployment**

- **FR-018**: System MUST deploy to a managed cloud Kubernetes service
  (AKS, GKE, or OKE).
- **FR-019**: System MUST have a CI/CD pipeline via GitHub Actions that
  builds, tests, and deploys on push to main.
- **FR-020**: Monitoring and logging MUST be configured on the cloud
  cluster.

**Cross-Cutting**

- **FR-021**: System MUST preserve all Phase 1-4 functionality (CRUD,
  auth, chatbot, MCP tools).
- **FR-022**: The chatbot MUST understand natural language commands for
  all new features (priorities, tags, search, filter, sort, due dates,
  reminders, recurring tasks).

### Key Entities

- **Task**: Extended with priority (high/medium/low), tags (list of
  strings), due_date (datetime, nullable), reminder_offset (duration,
  nullable), recurrence (none/daily/weekly/monthly), is_recurring
  (boolean).
- **TaskEvent**: event_type, task_id, task_data, user_id, timestamp.
  Published to Kafka via Dapr Pub/Sub.
- **ReminderJob**: task_id, user_id, remind_at, status
  (scheduled/fired/cancelled). Managed by Dapr Jobs API.
- **Conversation**: Existing entity from Phase 3. Optionally managed
  via Dapr State API.
- **Message**: Existing entity from Phase 3, unchanged.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign priority and tags to a task in under 10
  seconds via the UI or a single chatbot message.
- **SC-002**: Search returns matching results in under 2 seconds for a
  list of up to 1000 tasks per user.
- **SC-003**: Reminders fire within 30 seconds of the scheduled time.
- **SC-004**: Recurring tasks generate the next occurrence within 60
  seconds of the current task being completed.
- **SC-005**: All task lifecycle events are published and consumed with
  at-least-once delivery (no silent data loss).
- **SC-006**: Local Minikube deployment completes and passes health
  checks within 5 minutes of running Helm install.
- **SC-007**: Cloud deployment is fully automated -- a push to main
  results in a live deployment within 15 minutes.
- **SC-008**: All existing Phase 1-4 features continue to work without
  regression after Phase 5 changes.
- **SC-009**: System uptime on cloud cluster is 99%+ during normal
  operation.
- **SC-010**: Swapping Kafka for another message broker requires only
  Dapr component configuration changes, zero code changes.

## Assumptions

- The user has a working Phase 4 deployment (Docker images, Helm charts,
  Minikube setup) as the starting point.
- Neon Serverless PostgreSQL remains the database for task and user data.
- Better Auth with JWT remains the authentication mechanism.
- OpenAI Agents SDK and MCP Server from Phase 3 remain the AI framework.
- Cloud provider free tier or credits are available for deployment.
- Browser Notification API is used for reminder notifications on the
  frontend.
- Dapr Jobs API (v1.0-alpha1) is available in the Dapr version deployed.
