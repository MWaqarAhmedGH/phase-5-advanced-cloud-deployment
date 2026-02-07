# Tasks: Advanced Cloud Deployment

**Input**: Design documents from `/specs/001-advanced-cloud-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included per Constitution Principle V (Test-First TDD).

**Organization**: Tasks grouped by user story. Each story is independently testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US7)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `frontend/components/`
- **Infrastructure**: `helm/`, `dapr-components/`, `.github/workflows/`
- **Tests**: `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Copy Phase 4 codebase, add new dependencies, initialize project structure for Phase 5.

- [ ] T001 Copy Phase 4 backend/ directory from phase-4-local-kubernetes-deployment into this project root
- [ ] T002 Copy Phase 4 frontend/ directory from phase-4-local-kubernetes-deployment into this project root
- [ ] T003 Copy Phase 4 helm/ directory from phase-4-local-kubernetes-deployment into this project root
- [ ] T004 Copy Phase 4 docker-compose.yml and .env.example from phase-4-local-kubernetes-deployment into this project root
- [ ] T005 [P] Create dapr-components/ directory with kafka-pubsub.yaml, statestore.yaml, kubernetes-secrets.yaml per contracts/dapr-components.md
- [ ] T006 [P] Create .github/workflows/ directory structure for CI/CD pipeline
- [ ] T007 [P] Add httpx dependency to backend/requirements.txt (or pyproject.toml) for Dapr HTTP calls
- [ ] T008 [P] Update backend/.env.example with new env vars: DAPR_HTTP_PORT=3500, KAFKA_PUBSUB_NAME=kafka-pubsub, STATE_STORE_NAME=statestore
- [ ] T009 [P] Update frontend/.env.example with NEXT_PUBLIC_SSE_ENDPOINT for reminder notifications

**Checkpoint**: Project structure matches plan.md. All Phase 4 code is present. New directories and dependencies added.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database migration for new fields, health endpoints, Dapr event publisher helper, and extended MCP tools. MUST complete before any user story.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T010 Create database migration script to ALTER TABLE tasks: add columns priority (varchar, default 'medium'), due_date (timestamptz, nullable), reminder_offset_minutes (integer, nullable), recurrence (varchar, default 'none'), is_recurring (boolean, default false) in backend/migrations/
- [ ] T011 Create database migration script to CREATE TABLE task_tags (id serial PK, task_id integer FK, tag varchar(50), UNIQUE(task_id, tag)) in backend/migrations/
- [ ] T012 Extend Task model in backend/app/models/task.py (or backend/models.py) with new fields: priority, due_date, reminder_offset_minutes, recurrence, is_recurring per data-model.md
- [ ] T013 Create TaskTag model in backend/app/models/task_tag.py (or extend backend/models.py) with fields: id, task_id, tag per data-model.md
- [ ] T014 Create event publisher service in backend/app/services/event_publisher.py: async function publish_event(topic, event_type, task_data, user_id) that POSTs to Dapr Pub/Sub HTTP API at http://localhost:3500/v1.0/publish/{pubsub_name}/{topic}
- [ ] T015 [P] Create health endpoints in backend/app/routes/health.py: GET /health (liveness) returns 200, GET /ready (readiness) checks DB connection and Dapr sidecar reachability
- [ ] T016 [P] Create Dapr subscription endpoint in backend/app/main.py: GET /dapr/subscribe returns subscription list for task-events and reminders topics per contracts/dapr-components.md
- [ ] T017 [P] Create event handler stubs in backend/app/routes/events.py: POST /api/events/task and POST /api/events/reminder that log received events and return {"status": "SUCCESS"}
- [ ] T018 Extend MCP tools in backend/app/mcp/tools.py (or backend/mcp/tools.py): update add_task tool to accept optional params priority, tags, due_date, reminder_offset_minutes, recurrence
- [ ] T019 Extend MCP tools in backend/app/mcp/tools.py (or backend/mcp/tools.py): update list_tasks tool to accept optional params priority, tag, search, sort
- [ ] T020 Extend MCP tools in backend/app/mcp/tools.py (or backend/mcp/tools.py): update update_task tool to accept optional params priority, tags, due_date, reminder_offset_minutes, recurrence
- [ ] T021 Write contract test in backend/tests/contract/test_health.py: verify GET /health returns 200, GET /ready returns 200 when DB is connected

**Checkpoint**: Database has new columns/tables. Models updated. Event publisher ready. MCP tools extended. Health endpoints working. Foundation ready for user stories.

---

## Phase 3: User Story 1 - Prioritize and Categorize Tasks (Priority: P1)

**Goal**: Users can assign priority levels (high/medium/low) and tags to tasks via UI and chatbot.

**Independent Test**: Create a task with priority "high" and tag "work", verify both persist and display correctly.

### Tests for US1

- [ ] T022 [P] [US1] Write contract test in backend/tests/contract/test_task_priority.py: POST /api/{user_id}/tasks with priority field returns task with correct priority; defaults to "medium" if omitted
- [ ] T023 [P] [US1] Write contract test in backend/tests/contract/test_task_tags.py: POST /api/{user_id}/tasks/{id}/tags adds tags; DELETE /api/{user_id}/tasks/{id}/tags/{tag} removes tag; GET returns task with tags array

### Implementation for US1

- [ ] T024 [US1] Update task creation endpoint in backend/app/routes/tasks.py (or backend/routes/tasks.py): accept priority field in POST /api/{user_id}/tasks, validate against allowed values (high/medium/low), default to "medium"
- [ ] T025 [US1] Update task update endpoint in backend/app/routes/tasks.py: accept priority field in PUT /api/{user_id}/tasks/{id}
- [ ] T026 [US1] Add tag management endpoints in backend/app/routes/tasks.py: POST /api/{user_id}/tasks/{id}/tags (add tags), DELETE /api/{user_id}/tasks/{id}/tags/{tag} (remove tag)
- [ ] T027 [US1] Update GET /api/{user_id}/tasks response to include priority field and tags array (join TaskTag table) in backend/app/routes/tasks.py
- [ ] T028 [US1] Integrate event publisher: publish "task.created" and "task.updated" events with priority and tags data when tasks are created/updated in backend/app/routes/tasks.py
- [ ] T029 [P] [US1] Update TaskCard component in frontend/components/TaskCard.tsx (or equivalent): display priority badge (color-coded) and tag chips
- [ ] T030 [P] [US1] Update TaskForm component in frontend/components/TaskForm.tsx (or equivalent): add priority dropdown (high/medium/low) and tag input field
- [ ] T031 [US1] Update API client in frontend/lib/api.ts: add priority and tags params to createTask and updateTask functions; add addTag and removeTag functions

**Checkpoint**: Users can set priority and tags on tasks via UI. Chatbot understands "Add a high priority task tagged work". Events include priority/tag data.

---

## Phase 4: User Story 2 - Search, Filter, and Sort Tasks (Priority: P1)

**Goal**: Users can search by keyword, filter by status/priority/tag/date, and sort tasks.

**Independent Test**: Create 10+ tasks with varied attributes, search for a keyword, filter by priority, sort by due date. Verify correct results.

### Tests for US2

- [ ] T032 [P] [US2] Write contract test in backend/tests/contract/test_task_search.py: GET /api/{user_id}/tasks?search=groceries returns only matching tasks; GET with priority=high returns only high-priority tasks; GET with sort=due_date returns ordered results

### Implementation for US2

- [ ] T033 [US2] Extend GET /api/{user_id}/tasks in backend/app/routes/tasks.py: add query params search (ILIKE on title+description), priority, tag, status, sort (due_date/priority/created_at/title), order (asc/desc), due_from, due_to per contracts/rest-api.md
- [ ] T034 [US2] Implement search/filter/sort SQL query builder in backend/app/routes/tasks.py: compose WHERE clauses from query params, ORDER BY from sort param, handle tag filter via JOIN on task_tags
- [ ] T035 [P] [US2] Create TaskFilters component in frontend/components/TaskFilters.tsx: search input, priority dropdown, status dropdown, tag filter, date range picker
- [ ] T036 [P] [US2] Create TaskSort component in frontend/components/TaskSort.tsx: sort dropdown (due date, priority, created, alphabetical) with asc/desc toggle
- [ ] T037 [US2] Update task list page in frontend/app/page.tsx: integrate TaskFilters and TaskSort, pass query params to API client, re-fetch on filter/sort change
- [ ] T038 [US2] Update API client in frontend/lib/api.ts: add search, priority, tag, status, sort, order, due_from, due_to params to getTasks function

**Checkpoint**: Users can search, filter by any attribute, and sort tasks. Chatbot responds to "Show my high priority tasks".

---

## Phase 5: User Story 5 - Event-Driven Architecture with Kafka and Dapr (Priority: P1)

**Goal**: All task lifecycle events flow through Kafka via Dapr Pub/Sub. Consumer services process events independently.

**Independent Test**: Create a task, verify "task.created" event is published to Kafka topic via Dapr and consumed by the event handler.

### Tests for US5

- [ ] T039 [P] [US5] Write integration test in backend/tests/integration/test_events.py: mock Dapr HTTP endpoint, create a task via API, verify publish_event was called with correct topic and event_type

### Implementation for US5

- [ ] T040 [US5] Wire event publishing into all task CRUD operations in backend/app/routes/tasks.py: call publish_event after create (task.created), update (task.updated), complete (task.completed), delete (task.deleted)
- [ ] T041 [US5] Implement audit event handler in backend/app/routes/events.py: POST /api/events/task receives task events, logs them with structured JSON (timestamp, user_id, event_type, task_id)
- [ ] T042 [US5] Verify Dapr Pub/Sub component config in dapr-components/kafka-pubsub.yaml points to correct Kafka broker (Redpanda for local, Strimzi for cloud)
- [ ] T043 [US5] Update docker-compose.yml: add Redpanda service container for local Kafka-compatible development (image: redpandadata/redpanda, ports: 9092, 9093)
- [ ] T044 [US5] Update docker-compose.yml: add Dapr sidecar containers for backend and frontend services with correct app-id, app-port, and component mounts

**Checkpoint**: Task events flow through Kafka via Dapr. Audit consumer logs all events. No direct Kafka client libraries in application code.

---

## Phase 6: User Story 3 - Due Dates and Time Reminders (Priority: P2)

**Goal**: Users can set deadlines and receive timed reminders before tasks are due.

**Independent Test**: Create a task with due date 5 minutes from now and reminder at 2 minutes before. Verify reminder notification fires.

### Tests for US3

- [ ] T045 [P] [US3] Write contract test in backend/tests/contract/test_task_due_date.py: POST task with due_date stores it; GET task returns due_date; task with past due_date is marked overdue in response
- [ ] T046 [P] [US3] Write unit test in backend/tests/unit/test_reminder_service.py: schedule_reminder calls Dapr Jobs API with correct dueTime; cancel_reminder calls DELETE on Dapr Jobs API

### Implementation for US3

- [ ] T047 [US3] Update task creation/update endpoints in backend/app/routes/tasks.py: accept due_date and reminder_offset_minutes fields; validate reminder requires due_date
- [ ] T048 [US3] Create reminder service in backend/app/services/reminder_service.py: async schedule_reminder(task_id, user_id, due_date, offset_minutes) POSTs to Dapr Jobs API at http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}; async cancel_reminder(task_id) DELETEs the job
- [ ] T049 [US3] Create jobs callback handler in backend/app/routes/jobs.py: POST /api/jobs/trigger receives Dapr job callback, publishes "reminder.due" event to reminders topic via event_publisher
- [ ] T050 [US3] Implement reminder event handler in backend/app/routes/events.py: POST /api/events/reminder receives reminder events, checks if task still exists, prepares notification payload
- [ ] T051 [US3] Create notification service in backend/app/services/notification_service.py: SSE endpoint GET /api/{user_id}/notifications/stream that pushes reminder events to connected frontend clients
- [ ] T052 [US3] Wire reminder scheduling: when task is created/updated with due_date + reminder_offset, call schedule_reminder; when task is deleted, call cancel_reminder in backend/app/routes/tasks.py
- [ ] T053 [P] [US3] Update TaskForm component in frontend/components/TaskForm.tsx: add date/time picker for due_date and reminder offset selector
- [ ] T054 [P] [US3] Update TaskCard component in frontend/components/TaskCard.tsx: display due date, show overdue indicator for past due dates
- [ ] T055 [US3] Create SSE client in frontend/lib/sse.ts: connect to GET /api/{user_id}/notifications/stream, parse incoming reminder events
- [ ] T056 [US3] Create notification utility in frontend/lib/notifications.ts: request browser Notification permission, show desktop notification when reminder event received via SSE
- [ ] T057 [P] [US3] Create ReminderBanner component in frontend/components/ReminderBanner.tsx: in-app notification banner that appears when a reminder fires

**Checkpoint**: Users can set due dates and reminders. Reminders fire via Dapr Jobs > Kafka > SSE > browser notification. Overdue tasks are visually marked.

---

## Phase 7: User Story 4 - Recurring Tasks (Priority: P2)

**Goal**: Tasks auto-reschedule after completion based on recurrence pattern (daily/weekly/monthly).

**Independent Test**: Create a weekly recurring task, complete it, verify a new task is automatically created for the next week.

### Tests for US4

- [ ] T058 [P] [US4] Write unit test in backend/tests/unit/test_recurring_service.py: calculate_next_due_date returns correct next date for daily (+1 day), weekly (+7 days), monthly (+1 month); create_next_occurrence creates task with same title, description, priority, tags and new due_date

### Implementation for US4

- [ ] T059 [US4] Update task creation/update endpoints in backend/app/routes/tasks.py: accept recurrence field, validate recurrence requires due_date, set is_recurring = (recurrence != "none")
- [ ] T060 [US4] Create recurring task service in backend/app/services/recurring_service.py: calculate_next_due_date(current_due, recurrence) computes next occurrence; create_next_occurrence(task) creates a new task with incremented due_date, same title/description/priority/tags, recurrence preserved
- [ ] T061 [US4] Implement recurring task consumer in backend/app/routes/events.py: when task.completed event arrives for a recurring task, call recurring_service.create_next_occurrence to spawn the next task
- [ ] T062 [US4] Ensure original completed recurring task stays in completed state (do not delete or modify it) in backend/app/services/recurring_service.py
- [ ] T063 [US4] Wire delete handling: when a recurring task is deleted, do NOT create future occurrences (event consumer checks task existence before spawning) in backend/app/routes/events.py
- [ ] T064 [P] [US4] Update TaskForm component in frontend/components/TaskForm.tsx: add recurrence dropdown (none/daily/weekly/monthly), disable recurrence when no due date is set
- [ ] T065 [P] [US4] Update TaskCard component in frontend/components/TaskCard.tsx: show recurrence indicator icon/badge on recurring tasks

**Checkpoint**: Completing a recurring task auto-creates the next occurrence. Chatbot understands "Add weekly meeting every Monday". Deleting stops future occurrences.

---

## Phase 8: User Story 6 - Local Kubernetes Deployment with Dapr (Priority: P2)

**Goal**: Full system (frontend, backend, Kafka, Dapr) deploys to Minikube with all Dapr building blocks functional.

**Independent Test**: Run `helm install` on Minikube, verify all pods running, Dapr sidecars injected, chatbot works, events flow through Kafka.

### Implementation for US6

- [ ] T066 [US6] Update backend Dockerfile in backend/Dockerfile: ensure multi-stage build, health check instruction, non-root user, port 8000 exposed
- [ ] T067 [US6] Update frontend Dockerfile in frontend/Dockerfile: ensure multi-stage build with Next.js standalone output, non-root user, port 3000 exposed
- [ ] T068 [US6] Update Helm chart backend-deployment.yaml in helm/todo-app/templates/ (or helm/todo-chatbot/templates/): add Dapr annotations (dapr.io/enabled, dapr.io/app-id=backend-service, dapr.io/app-port=8000), add readiness/liveness probes pointing to /health and /ready
- [ ] T069 [US6] Update Helm chart frontend-deployment.yaml in helm/todo-app/templates/ (or helm/todo-chatbot/templates/): add Dapr annotations (dapr.io/enabled, dapr.io/app-id=frontend-service, dapr.io/app-port=3000)
- [ ] T070 [US6] Create Helm values for Redpanda in helm/redpanda-values.yaml: single replica, 1 CPU, 1Gi memory, no TLS, ephemeral storage per research.md
- [ ] T071 [US6] Update Helm chart values.yaml: add Dapr component references, Kafka broker URL (redpanda.redpanda.svc.cluster.local:9093), image pull policy IfNotPresent for local
- [ ] T072 [US6] Create Kubernetes Secret templates in helm/todo-app/templates/secrets.yaml: db-credentials (connection-string), app-secrets (better-auth-secret, openai-api-key)
- [ ] T073 [US6] Copy dapr-components/*.yaml into helm/todo-app/templates/ or deploy as separate kubectl apply step; ensure kafka-pubsub points to Redpanda broker
- [ ] T074 [US6] Update quickstart.md with exact Minikube deployment commands: minikube start, dapr init -k, helm install redpanda, kubectl create secret, kubectl apply -f dapr-components/, helm install todo-app
- [ ] T075 [US6] Test full deployment on Minikube: verify all pods Running, Dapr sidecars present, create task via chatbot, verify Kafka event via rpk topic consume

**Checkpoint**: Full system runs on Minikube. All Dapr building blocks operational (Pub/Sub, State, Secrets, Service Invocation). Chatbot fully functional. Events flowing through Kafka.

---

## Phase 9: User Story 7 - Cloud Kubernetes Deployment with CI/CD (Priority: P3)

**Goal**: System deployed to managed cloud K8s with automated CI/CD via GitHub Actions.

**Independent Test**: Push commit to main, verify pipeline builds images, deploys to cloud, chatbot accessible via public URL.

### Implementation for US7

- [ ] T076 [US7] Create CI/CD pipeline in .github/workflows/ci-cd.yaml: jobs for test (pytest + npm test), build-push (docker build + push to ghcr.io), deploy (helm upgrade --install --atomic) per research.md
- [ ] T077 [US7] Create cloud Helm values file in helm/todo-app/values-cloud.yaml: ghcr.io image registry, LoadBalancer service type, cloud Kafka broker URL, resource limits (CPU/memory), ingress configuration
- [ ] T078 [US7] Create Strimzi Kafka cluster manifest in helm/kafka-cluster.yaml: single replica, ephemeral storage, internal listener on port 9092 per research.md
- [ ] T079 [US7] Configure GitHub repository secrets documentation in README.md: list required secrets (KUBECONFIG or cloud provider credentials, OPENAI_API_KEY, DATABASE_URL, BETTER_AUTH_SECRET)
- [ ] T080 [US7] Add deployment verification step in .github/workflows/ci-cd.yaml: after helm deploy, curl health endpoint to verify deployment success; on failure, helm rollback
- [ ] T081 [US7] Configure monitoring: add structured JSON logging format in backend/app/main.py logging config; document cloud provider monitoring setup (Azure Monitor / GCP Cloud Logging / OCI Logging) in README.md
- [ ] T082 [US7] Test cloud deployment end-to-end: deploy to AKS/GKE/OKE, verify public URL, create task via chatbot, verify Kafka events, verify monitoring logs

**Checkpoint**: System live on cloud K8s. CI/CD deploys on push to main. Monitoring captures logs. Public URL accessible.

---

## Phase 10: Polish and Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and quality improvements.

- [ ] T083 [P] Update README.md with comprehensive project documentation: architecture overview, local setup, cloud deployment, environment variables, API reference
- [ ] T084 [P] Update docker-compose.yml to include all services (frontend, backend, Redpanda, Dapr sidecars) for one-command local development
- [ ] T085 Verify Phase 1-4 backward compatibility: run all existing tests, verify basic CRUD, auth, and chatbot still work after Phase 5 changes
- [ ] T086 Run full integration test: create task with all new fields (priority, tags, due date, reminder, recurrence) via chatbot, verify event flow, verify reminder fires, verify recurring task spawns
- [ ] T087 [P] Clean up code: remove unused imports, ensure consistent error handling, verify no hardcoded secrets in any file
- [ ] T088 Security review: verify all secrets accessed via Dapr Secrets or env vars, no credentials in source code, JWT auth enforced on all endpoints

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies -- start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 -- BLOCKS all user stories
- **Phase 3 (US1 Priorities/Tags)**: Depends on Phase 2
- **Phase 4 (US2 Search/Filter/Sort)**: Depends on Phase 2; benefits from US1 (priority/tag data to filter)
- **Phase 5 (US5 Event Architecture)**: Depends on Phase 2
- **Phase 6 (US3 Due Dates/Reminders)**: Depends on Phase 2 + Phase 5 (needs event infrastructure for reminders)
- **Phase 7 (US4 Recurring Tasks)**: Depends on Phase 2 + Phase 5 (needs event infrastructure) + Phase 6 (needs due dates)
- **Phase 8 (US6 Local K8s)**: Depends on all feature phases (3-7) being code-complete
- **Phase 9 (US7 Cloud Deployment)**: Depends on Phase 8 (local K8s validated first)
- **Phase 10 (Polish)**: Depends on all prior phases

### User Story Dependencies

```text
Phase 2 (Foundation)
  ├── US1 (Priorities/Tags) ──────────────────┐
  ├── US2 (Search/Filter/Sort) ───────────────┤
  └── US5 (Event Architecture) ───────────────┤
       ├── US3 (Due Dates/Reminders) ─────────┤
       │    └── US4 (Recurring Tasks) ─────────┤
       │                                       │
       └───────────────────────── US6 (Local K8s) ── US7 (Cloud) ── Polish
```

### Parallel Opportunities

**Within Phase 1 (Setup)**:
- T005, T006, T007, T008, T009 can all run in parallel

**Within Phase 2 (Foundation)**:
- T015, T016, T017 can run in parallel (different files)

**Within Phase 3 (US1)**:
- T022, T023 (tests) in parallel
- T029, T030 (frontend) in parallel with backend work

**Within Phase 4 (US2)**:
- T035, T036 (frontend components) in parallel

**After Foundation**:
- US1, US2, US5 can start in parallel (all only depend on Phase 2)

---

## Implementation Strategy

### MVP First (US1 + US5 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 (Priorities/Tags)
4. Complete Phase 5: US5 (Event Architecture)
5. **STOP and VALIDATE**: Tasks have priorities/tags, events flow through Kafka
6. Demo-ready: basic advanced features + event-driven architecture

### Incremental Delivery

1. Setup + Foundational > Foundation ready
2. US1 (Priorities/Tags) > Demo increment 1
3. US2 (Search/Filter/Sort) > Demo increment 2
4. US5 (Event Architecture) > Demo increment 3
5. US3 (Due Dates/Reminders) > Demo increment 4
6. US4 (Recurring Tasks) > Demo increment 5
7. US6 (Local K8s) > Demo increment 6
8. US7 (Cloud Deployment) > Demo increment 7
9. Polish > Final submission

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Constitution Principle V (TDD): tests written before implementation in each story phase
- All Dapr interactions use HTTP API at localhost:3500 (Constitution Principle III)
- No direct Kafka client libraries in application code
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
