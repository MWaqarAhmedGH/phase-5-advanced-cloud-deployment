# Data Model: Advanced Cloud Deployment

**Feature**: 001-advanced-cloud-deployment
**Date**: 2026-02-07

## Entity Relationship Overview

```text
User (1) ──── (*) Task
Task (1) ──── (*) TaskTag (join table)
Task (1) ──── (0..1) ReminderJob
Task (1) ──── (*) TaskEvent (audit log)
User (1) ──── (*) Conversation
Conversation (1) ──── (*) Message
```

## Entities

### Task (Extended from Phase 2-3)

Existing fields preserved. New fields added for Phase 5.

| Field            | Type                          | Nullable | Default  | Notes                               |
|------------------|-------------------------------|----------|----------|-------------------------------------|
| id               | integer                       | no       | auto     | Primary key (existing)              |
| user_id          | string                        | no       | -        | FK to users.id (existing)           |
| title            | string(200)                   | no       | -        | (existing)                          |
| description      | text                          | yes      | null     | (existing)                          |
| completed        | boolean                       | no       | false    | (existing)                          |
| created_at       | datetime (tz)                 | no       | now()    | (existing)                          |
| updated_at       | datetime (tz)                 | no       | now()    | (existing)                          |
| **priority**     | **enum(high,medium,low)**     | **no**   | **medium** | **NEW: Task importance level**    |
| **due_date**     | **datetime (tz)**             | **yes**  | **null** | **NEW: Task deadline**              |
| **reminder_offset_minutes** | **integer**        | **yes**  | **null** | **NEW: Minutes before due_date**    |
| **recurrence**   | **enum(none,daily,weekly,monthly)** | **no** | **none** | **NEW: Repeat pattern**        |
| **is_recurring**  | **boolean**                  | **no**   | **false** | **NEW: Derived from recurrence**   |

**Indexes**:
- `idx_task_user_id` on user_id (existing)
- `idx_task_completed` on completed (existing)
- `idx_task_priority` on priority (NEW)
- `idx_task_due_date` on due_date (NEW)
- `idx_task_user_priority` on (user_id, priority) (NEW, composite)

**Validation Rules**:
- priority MUST be one of: high, medium, low
- recurrence MUST be one of: none, daily, weekly, monthly
- If recurrence != none, due_date MUST NOT be null
- reminder_offset_minutes MUST be >= 0 if set
- is_recurring = (recurrence != none)

**State Transitions**:
- pending → completed (mark complete)
- completed → pending (unmark complete)
- On completion of recurring task → new task created with next due_date

---

### TaskTag (NEW)

Many-to-many relationship between Task and free-form tags.

| Field    | Type        | Nullable | Default | Notes               |
|----------|-------------|----------|---------|---------------------|
| id       | integer     | no       | auto    | Primary key         |
| task_id  | integer     | no       | -       | FK to tasks.id      |
| tag      | string(50)  | no       | -       | Tag label           |

**Indexes**:
- `idx_tasktag_task_id` on task_id
- `idx_tasktag_tag` on tag
- `uq_tasktag_task_tag` UNIQUE on (task_id, tag)

**Validation Rules**:
- tag MUST be lowercase, trimmed, 1-50 characters
- No duplicate (task_id, tag) pairs

---

### TaskEvent (NEW -- Kafka event payload)

Not stored in primary DB. Published to Kafka via Dapr Pub/Sub.
Optionally stored by audit consumer.

| Field      | Type        | Nullable | Notes                            |
|------------|-------------|----------|----------------------------------|
| event_type | string      | no       | created/updated/completed/deleted |
| task_id    | integer     | no       | The task that changed            |
| task_data  | object      | no       | Full task snapshot at event time |
| user_id    | string      | no       | Who triggered the event          |
| timestamp  | datetime    | no       | When the event occurred          |

**Topics**:
- `task-events`: All task lifecycle events
- `reminders`: Reminder due events

---

### ReminderJob (NEW -- Dapr Jobs API managed)

Not stored in primary DB. Managed by Dapr Jobs API scheduler.

| Field      | Type        | Nullable | Notes                     |
|------------|-------------|----------|---------------------------|
| job_name   | string      | no       | `reminder-task-{task_id}` |
| task_id    | integer     | no       | FK to tasks.id            |
| user_id    | string      | no       | Who to notify             |
| remind_at  | datetime    | no       | Exact time to fire        |
| status     | string      | no       | scheduled/fired/cancelled |

**Lifecycle**:
- Created when user sets reminder on a task
- Fired by Dapr at remind_at time (callback to /api/jobs/trigger)
- Cancelled if task is deleted or reminder is removed

---

### Conversation (Existing from Phase 3)

| Field      | Type        | Nullable | Default | Notes          |
|------------|-------------|----------|---------|----------------|
| id         | integer     | no       | auto    | Primary key    |
| user_id    | string      | no       | -       | FK to users.id |
| created_at | datetime    | no       | now()   |                |
| updated_at | datetime    | no       | now()   |                |

Unchanged. Optionally cached via Dapr State API for faster access.

---

### Message (Existing from Phase 3)

| Field           | Type    | Nullable | Default | Notes              |
|-----------------|---------|----------|---------|--------------------|
| id              | integer | no       | auto    | Primary key        |
| conversation_id | integer | no       | -       | FK to conversations |
| user_id         | string  | no       | -       | FK to users.id     |
| role            | string  | no       | -       | user/assistant     |
| content         | text    | no       | -       | Message body       |
| created_at      | datetime| no       | now()   |                    |

Unchanged.

---

## Migration Strategy

Phase 5 requires database migrations on the existing Neon PostgreSQL:

1. **ALTER TABLE tasks ADD COLUMN** priority, due_date,
   reminder_offset_minutes, recurrence, is_recurring
2. **CREATE TABLE** task_tags
3. **CREATE INDEX** for new columns
4. **Backfill**: Set priority='medium' and recurrence='none' for
   existing tasks (non-breaking defaults)

Migration MUST be backward-compatible with Phase 3-4 code until
the new code is deployed.
