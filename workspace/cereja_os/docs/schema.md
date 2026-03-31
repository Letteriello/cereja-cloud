# Cereja OS - Database Schema

## Overview

SQLAlchemy 2.0 models with SQLite backend. Multi-tenant isolation via `tenant_id` on all scoped tables.

## Tables

### tasks
Main task/subtask table with soft delete.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | UUID |
| title | String(200) | Required |
| description | Text | |
| status | String(20) | pending/in_progress/review/done/cancelled |
| urgency | String(20) | high/medium/low |
| team | String(20) | FRONTEND/BACKEND/DEVOPS/QA/DESIGN |
| tenant_id | String(36) FK | Tenant isolation |
| assignee_id | String(36) | Agent assigned |
| parent_task_id | String(36) FK | Self-reference for subtasks |
| deleted_at | DateTime | Soft delete marker |
| created_at/updated_at | DateTime | |

Indexes: status, deleted_at, parent_task_id, tenant_id

### tenants
Multi-tenant root table.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | |
| name | String(100) | |
| plan | String(20) | basic/pro/enterprise |
| is_active | Boolean | |

### users
User accounts with password hashing.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | |
| email | String(255) | Unique per tenant |
| name | String(100) | |
| password_hash | String(64) | SHA-256 |
| salt | String(32) | Per-user salt |
| role | String(20) | admin/member |
| tenant_id | String(36) FK | |

### agents
AI agent registry.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | |
| name | String(100) | Agent display name |
| role | String(50) | executor/planner/reviewer/patrol |
| agent_type | String(50) | ai_escritor/ai_pesquisador/etc |
| team | String(20) | FRONTEND/BACKEND/etc |
| status | String(20) | active/inactive/maintenance |
| capabilities | Text | JSON array of skill names |
| score | Float | Overall performance score |
| tasks_completed | Integer | |
| tasks_rejected | Integer | |

### rules
Business rule engine for task automation.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | |
| name | String(100) | |
| rule_type | String(50) | task_transition/assignment/notification/scoring |
| target | String(50) | task/subtask/agent/team |
| conditions | Text | JSON conditions |
| actions | Text | JSON action list |
| priority | Integer | Evaluation order |

### scores
Performance score records.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | |
| subject_type | String(20) | agent/team/task |
| subject_id | String(36) | |
| tenant_id | String(36) | |
| score_type | String(50) | quality/speed/rework/overall |
| value | Float | Score value |
| max_value | Float | Max possible (default 5.0) |
| weight | Float | For weighted averages |

### logs
Activity audit log.

| Column | Type | Notes |
|--------|------|-------|
| id | String(36) PK | |
| tenant_id | String(36) | |
| subject_type | String(20) | agent/task/system/user |
| subject_id | String(36) | |
| action | String(50) | created/updated/deleted/submitted/approved/rejected |
| category | String(30) | coding/delivery/blocked/reflection/review/patrol/plan |
| description | Text | Human-readable log message |
| details | Text | JSON with extra context |
| task_id/subtask_id | String(36) | Related entities |

## Relationships

- Task → Tenant (many-to-one, tenant_id FK)
- Task → Task (self-referential for subtasks, parent_task_id FK)
- User → Tenant (many-to-one, tenant_id FK)
- Agent → no tenant FK (system-level entity)
- Rule → no FK (independent)
- Score → Tenant (many-to-one)
- Log → Tenant (many-to-one)

## Migrations

Alembic migrations in `migrations/versions/`:
- `1ae5eb6ebf1d_initial_models.py` - tenants, users
- `2a3b4c5d_complete_schema.py` - tasks, agents, rules, scores, logs

Apply with: `alembic upgrade head`
