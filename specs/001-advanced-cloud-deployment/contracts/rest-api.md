# REST API Contracts: Advanced Cloud Deployment

**Feature**: 001-advanced-cloud-deployment
**Date**: 2026-02-07
**Base URL**: `http://localhost:8000` (local) / via Dapr service invocation

All endpoints require JWT token: `Authorization: Bearer <token>`

## Extended Task Endpoints

### GET /api/{user_id}/tasks

List tasks with search, filter, and sort support.

**Query Parameters** (all optional):

| Param    | Type   | Description                                | Example           |
|----------|--------|--------------------------------------------|-------------------|
| status   | string | Filter: all, pending, completed            | `?status=pending` |
| priority | string | Filter: high, medium, low                  | `?priority=high`  |
| tag      | string | Filter by tag                              | `?tag=work`       |
| search   | string | Keyword search in title and description    | `?search=groceries` |
| sort     | string | Sort: due_date, priority, created_at, title | `?sort=due_date` |
| order    | string | Sort direction: asc, desc (default: asc)   | `?order=desc`     |
| due_from | string | Filter: due date >= (ISO 8601)             | `?due_from=2026-02-07` |
| due_to   | string | Filter: due date <= (ISO 8601)             | `?due_to=2026-02-14`  |

**Response** (200):
```json
[
  {
    "id": 1,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "tags": ["home", "errands"],
    "due_date": "2026-02-08T10:00:00Z",
    "reminder_offset_minutes": 30,
    "recurrence": "weekly",
    "is_recurring": true,
    "created_at": "2026-02-07T09:00:00Z",
    "updated_at": "2026-02-07T09:00:00Z"
  }
]
```

---

### POST /api/{user_id}/tasks

Create a new task with optional priority, tags, due date, reminder,
and recurrence.

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "tags": ["home", "errands"],
  "due_date": "2026-02-08T10:00:00Z",
  "reminder_offset_minutes": 30,
  "recurrence": "weekly"
}
```

Required: `title`
Optional: all other fields (defaults: priority=medium, tags=[],
due_date=null, reminder_offset_minutes=null, recurrence=none)

**Response** (201): Created task object.

**Side Effects**:
- Publishes `task.created` event to `task-events` topic via Dapr.
- If reminder_offset_minutes set AND due_date set, schedules Dapr Job.

**Errors**:
- 400: title empty, invalid priority, recurrence without due_date
- 401: Missing/invalid JWT
- 422: Validation errors

---

### PUT /api/{user_id}/tasks/{id}

Update task. Accepts partial updates.

**Request Body** (all optional):
```json
{
  "title": "Updated title",
  "description": "Updated desc",
  "priority": "low",
  "tags": ["work"],
  "due_date": "2026-02-10T14:00:00Z",
  "reminder_offset_minutes": 15,
  "recurrence": "daily"
}
```

**Response** (200): Updated task object.

**Side Effects**:
- Publishes `task.updated` event via Dapr.
- If reminder changed, cancels old Dapr Job and schedules new one.

---

### PATCH /api/{user_id}/tasks/{id}/complete

Toggle task completion.

**Response** (200): Updated task object.

**Side Effects**:
- Publishes `task.completed` event via Dapr.
- If task is recurring AND being marked complete:
  - Recurring-task consumer creates next occurrence.

---

### DELETE /api/{user_id}/tasks/{id}

Delete a task.

**Response** (200): `{"task_id": 1, "status": "deleted"}`

**Side Effects**:
- Publishes `task.deleted` event via Dapr.
- Cancels any scheduled Dapr reminder Job for this task.

---

### POST /api/{user_id}/tasks/{id}/tags

Add tags to a task.

**Request Body**:
```json
{"tags": ["urgent", "meeting"]}
```

**Response** (200): Updated task object with tags.

---

### DELETE /api/{user_id}/tasks/{id}/tags/{tag}

Remove a specific tag from a task.

**Response** (200): Updated task object with remaining tags.

---

## Chat Endpoint (Extended)

### POST /api/{user_id}/chat

Send message and get AI response. Unchanged from Phase 3 except the
agent now has access to extended MCP tools.

**Request Body**:
```json
{
  "conversation_id": 1,
  "message": "Add a high priority task to buy groceries tagged home, due tomorrow at 10am"
}
```

**Response** (200):
```json
{
  "conversation_id": 1,
  "response": "I've created a high priority task 'Buy groceries' tagged 'home', due tomorrow at 10:00 AM.",
  "tool_calls": [
    {"tool": "add_task", "args": {"title": "Buy groceries", "priority": "high", "tags": ["home"], "due_date": "2026-02-08T10:00:00Z"}}
  ]
}
```

---

## Extended MCP Tools

### add_task (Extended)

| Parameter               | Type    | Required | Notes            |
|-------------------------|---------|----------|------------------|
| user_id                 | string  | yes      |                  |
| title                   | string  | yes      |                  |
| description             | string  | no       |                  |
| priority                | string  | no       | high/medium/low  |
| tags                    | array   | no       | list of strings  |
| due_date                | string  | no       | ISO 8601         |
| reminder_offset_minutes | integer | no       | minutes before   |
| recurrence              | string  | no       | none/daily/weekly/monthly |

### list_tasks (Extended)

| Parameter | Type   | Required | Notes                           |
|-----------|--------|----------|---------------------------------|
| user_id   | string | yes      |                                 |
| status    | string | no       | all/pending/completed           |
| priority  | string | no       | high/medium/low                 |
| tag       | string | no       | filter by tag                   |
| search    | string | no       | keyword search                  |
| sort      | string | no       | due_date/priority/title         |

### update_task (Extended)

| Parameter               | Type    | Required | Notes            |
|-------------------------|---------|----------|------------------|
| user_id                 | string  | yes      |                  |
| task_id                 | integer | yes      |                  |
| title                   | string  | no       |                  |
| description             | string  | no       |                  |
| priority                | string  | no       |                  |
| tags                    | array   | no       |                  |
| due_date                | string  | no       |                  |
| reminder_offset_minutes | integer | no       |                  |
| recurrence              | string  | no       |                  |

### complete_task / delete_task

Unchanged from Phase 3 but now trigger Kafka events via Dapr.

---

## Dapr Event Contracts

### task-events Topic

```json
{
  "event_type": "created | updated | completed | deleted",
  "task_id": 1,
  "task_data": { /* full task object snapshot */ },
  "user_id": "user123",
  "timestamp": "2026-02-07T12:00:00Z"
}
```

### reminders Topic

```json
{
  "task_id": 1,
  "title": "Buy groceries",
  "due_at": "2026-02-08T10:00:00Z",
  "remind_at": "2026-02-08T09:30:00Z",
  "user_id": "user123"
}
```

---

## Health Endpoints

### GET /health

Returns 200 if the service is alive.

### GET /ready

Returns 200 if the service is ready (DB connected, Dapr sidecar
reachable). Returns 503 if not ready.
