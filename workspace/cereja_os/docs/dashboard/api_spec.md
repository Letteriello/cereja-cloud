# SPEC - Dashboard API Endpoints
**Módulo:** Dashboard (Next.js Frontend)
**Task ID:** M4.3
**Autor:** AI-Escritor (Backend Developer)
**Data:** 2026-03-31

---

## 1. Visão Geral

O Dashboard Cereja OS é uma aplicação Next.js 14 (App Router) que serve como interface administrativa para gestão de equipes e tarefas. O dashboard consome APIs de duas origens:

1. **Next.js API Routes** (`/app/api/*`) — Handlers server-side do Next.js (mock data ou proxy)
2. **FastAPI Backend** (`/api/*`) — API real do Cereja OS (tarefas, auth, orquestrador)

**URL Base do Dashboard:** `https://dashboard.cereja.cloud`
**URL Base da API:** `https://cereja.cloud/api` (via nginx → FastAPI)

---

## 2. Arquitetura de Requisições

```
┌─────────────────────────────────────────────────────┐
│  Browser (React Client)                             │
└──────────────────┬──────────────────────────────────┘
                   │ fetch('/api/teams')
                   ▼
┌─────────────────────────────────────────────────────┐
│  Next.js Server (API Routes)                        │
│  Location: dashboard/app/api/*                      │
│  - /api/teams/route.ts     → mock static data       │
│  - /api/notifications/     → SSE stream mock        │
│  - /api/conversations/     → mock conversations     │
└──────────────────┬──────────────────────────────────┘
                   │ (algumas rotas fazem proxy para FastAPI)
                   ▼
┌─────────────────────────────────────────────────────┐
│  FastAPI Backend (Port 8000)                        │
│  - /api/tasks/*     → Task CRUD real                │
│  - /api/auth/*      → Auth JWT real                 │
│  - /api/orchestrator/* → Intent routing real        │
│  - /api/knowledge_base/* → KB real                  │
└─────────────────────────────────────────────────────┘
                   ▲
                   │ nginx reverse proxy (port 443)
                   ▼
┌─────────────────────────────────────────────────────┐
│  Nginx Reverse Proxy                                │
│  dashboard.cereja.cloud → Next.js :3000             │
│  cereja.cloud/api/*     → API/FastAPI :8000         │
│  telegram.cereja.cloud  → Telegram Bot :8080        │
└─────────────────────────────────────────────────────┘
```

---

## 3. Next.js API Routes (Mock/Static)

Estas rotas estão em `dashboard/app/api/*` e retornam dados mockados em ambiente de demonstração.

### 3.1 GET `/api/teams`

**Arquivo:** `dashboard/app/api/teams/route.ts`
**Método:** GET
**Descrição:** Retorna lista de times com líderes, agentes e tarefas (dados mockados).

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "dev",
      "name": "Dev",
      "emoji": "🏗️",
      "leader": {
        "id": "leader-dev",
        "name": "Carlos Silva",
        "role": "Tech Lead"
      },
      "agents": [
        {
          "id": "agent-1",
          "name": "Ana Costa",
          "specialty": "Backend",
          "status": "online"
        }
      ],
      "tasks": [
        { "id": "task-1", "title": "API REST Implementation", "status": "in_progress" }
      ],
      "activeTasks": 8
    }
  ]
}
```

### 3.2 GET `/api/notifications`

**Arquivo:** `dashboard/app/api/notifications/route.ts`
**Método:** GET (SSE - Server-Sent Events)
**Descrição:** Stream de notificações em tempo real via SSE.

**Headers de Response:**
```
Content-Type: text/event-stream
Cache-Control: no-cache, no-transform
Connection: keep-alive
X-Accel-Buffering: no
```

**Eventos SSE:**
```
data: {"type": "connected", "timestamp": "2026-03-31T..."}
data: {"type": "initial", "notifications": [...]}
data: {"type": "notification", "notification": {...}}
```

**POST `/api/notifications`:** Broadcast de notificação para todos os clientes conectados (para uso interno/API).

### 3.3 GET `/api/conversations`

**Arquivo:** `dashboard/app/api/conversations/route.ts`
**Método:** GET
**Descrição:** Lista conversas de WhatsApp/chat (mockado).

---

## 4. FastAPI Backend Endpoints (Reais)

O frontend consome estes endpoints via `lib/api.ts` (que aponta para `NEXT_PUBLIC_API_URL`). Em produção, `NEXT_PUBLIC_API_URL` deve ser `https://cereja.cloud/api`.

### 4.1 Tasks API (`/api/tasks`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/tasks` | Lista tarefas do tenant (não-deleted) |
| GET | `/api/tasks/{id}` | Detalhes de uma tarefa |
| POST | `/api/tasks` | Cria tarefa |
| PUT | `/api/tasks/{id}` | Atualiza tarefa |
| DELETE | `/api/tasks/{id}` | Soft delete (retorna 409 com opções se tiver subtasks) |
| POST | `/api/tasks/{id}/restore` | Restaura task deletada |
| POST | `/api/tasks/{id}/relocate-subtasks` | Move ou marca órfãs subtasks |
| DELETE | `/api/tasks/{id}/force-delete` | Força delete |
| GET | `/api/tasks/{id}/subtasks` | Lista subtasks |

**Response Task:**
```json
{
  "id": "string",
  "title": "string",
  "description": "string|null",
  "status": "pending|in_progress|review|done|cancelled",
  "urgency": "high|medium|low",
  "team": "string",
  "assignee_id": "string|null",
  "assignee_name": "string|null",
  "assignee_avatar": "string|null",
  "parent_task_id": "string|null",
  "has_subtasks": true|false,
  "subtask_count": 0,
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "deleted_at": "ISO8601|null"
}
```

### 4.2 Auth API (`/api/auth`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/login` | Login (retorna JWT) |
| POST | `/api/auth/register` | Registro |
| GET | `/api/auth/me` | Informações do usuário atual |
| POST | `/api/auth/refresh` | Refresh do token JWT |

**Nota:** `lib/api.ts` espera `/api/users/me` mas o backend implementa `/api/auth/me`. Verificar alinhamento.

### 4.3 Orchestrator API (`/api/orchestrator`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/orchestrator/route` | Classifica mensagem e cria task |
| GET | `/api/orchestrator/tasks/{id}` | Status de task do orquestrador |
| POST | `/api/orchestrator/route-manual` | Routing manual para team |
| GET | `/api/orchestrator/teams` | Status dos teams (contadores) |
| POST | `/api/orchestrator/classify` | Classifica intent (sem criar task) |
| POST | `/api/orchestrator/batch` | Routing em lote |

### 4.4 Knowledge Base API (`/api/knowledge_base`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/kb/articles` | Lista artigos |
| GET | `/api/kb/articles/{id}` | Detalhes de artigo |
| POST | `/api/kb/articles` | Cria artigo |
| PUT | `/api/kb/articles/{id}` | Atualiza artigo |
| DELETE | `/api/kb/articles/{id}` | Deleta artigo |
| GET | `/api/kb/search` | Busca artigos |
| GET | `/api/kb/categories` | Lista categorias |

### 4.5 Telegram Webhook (`/api/telegram`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/telegram/webhook` | Recebe updates do Telegram |

---

## 5. Client API (`lib/api.ts`)

**Arquivo:** `dashboard/lib/api.ts`

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'

// Endpoints esperados pelo frontend:
tenantApi.get()           → GET  /api/tenant        (NÃO IMPLEMENTADO - verificar)
usersApi.getCurrent()     → GET  /api/users/me     (mapeia para /api/auth/me)
usersApi.logout()         → POST /api/auth/logout  (NÃO IMPLEMENTADO)
teamsApi.list()           → GET  /api/teams        (Next.js route → mock)
tasksApi.list()           → GET  /api/tasks        (FastAPI)
tasksApi.create()         → POST /api/tasks        (FastAPI)
```

### Lacunas Identificadas:

| Endpoint Esperado | Status | Backend Real |
|-------------------|--------|--------------|
| `/api/tenant` | ❌ Não existe | `/api/auth/tenants/{id}` |
| `/api/users/me` | ⚠️ Mapeia para `/api/auth/me` | `/api/auth/me` ✅ |
| `/api/auth/logout` | ❌ Não existe | Não implementado |
| `/api/teams` | ⚠️ Mock (Next.js) | `/api/orchestrator/teams` existe mas usa formato diferente |

**Recomendação:** Criar Next.js API route `/app/api/tenant/route.ts` que faz proxy para `/api/auth/tenants/{id}` e implementar `/api/auth/logout` no FastAPI.

---

## 6. Nginx — Configuração de Routing

**Arquivo:** `infrastructure/docker/nginx.conf`

```nginx
server {
    listen 443 ssl http2;
    server_name dashboard.cereja.cloud;
    # Proxy para Next.js :3000
    location / {
        proxy_pass http://dashboard_backend;  # dashboard:3000
    }
}

server {
    listen 443 ssl http2;
    server_name api.cereja.cloud;
    # Proxy para FastAPI :8000
    location / {
        proxy_pass http://api_backend;  # api:8000
    }
}
```

### ⚠️ PROBLEMA CONHECIDO: `cereja.cloud/api/*`

O domínio `cereja.cloud` (sem subdomain) NÃO tem um server block dedicado no nginx. Requests GET para `/api/*` estão indo para o Vue app de **Cereja Numerologia** em vez do FastAPI. Requests POST para `/api/*` estão indo para o FastAPI (comportamento inconsistente).

**Correção necessária (DevOps):** Adicionar server block para `cereja.cloud` na porta 443 que faça proxy para o serviço apropriado (FastAPI para `/api/*`, Next.js para o resto).

---

## 7. Schemas (TypeScript)

### Team
```typescript
interface TeamLeader {
  id: string
  name: string
  role: string
  avatar?: string
}

interface Agent {
  id: string
  name: string
  specialty: string
  status: 'online' | 'busy' | 'offline'
  avatar?: string
}

interface Task {
  id: string
  title: string
  status: 'pending' | 'in_progress' | 'completed' | 'blocked'
}

interface Team {
  id: string
  name: string
  emoji: string
  leader: TeamLeader
  agents: Agent[]
  tasks: Task[]
  activeTasks: number
}
```

### Notification
```typescript
type NotificationType = 'order' | 'reservation' | 'message' | 'task' | 'system'

interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  timestamp: string
  read: boolean
  priority: 'low' | 'medium' | 'high'
  metadata?: Record<string, string | number | boolean>
}
```

---

## 8. Dashboard API Endpoints (FastAPI)

**Base Path:** `/api/dashboard`
**Authentication:** Bearer JWT token required
**Tenant Isolation:** All queries scoped by `tenant_id` from JWT

---

### 8.1 GET `/api/dashboard/overview`

**Descrição:** Retorna estatísticas consolidadas do tenant (tasks, agents, teams).

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `period` | `string` | `week` | Período: `day`, `week`, `month`, `all` |

**Response 200:**
```json
{
  "success": true,
  "data": {
    "period": "week",
    "tasks": {
      "total": 47,
      "by_status": {
        "pending": 12,
        "in_progress": 15,
        "review": 5,
        "done": 14,
        "cancelled": 1
      },
      "by_urgency": {
        "high": 8,
        "medium": 28,
        "low": 11
      },
      "completed_this_period": 9,
      "created_this_period": 14
    },
    "agents": {
      "total": 5,
      "online": 3,
      "busy": 1,
      "offline": 1
    },
    "teams": {
      "total": 4,
      "active": 3
    },
    "performance": {
      "avg_score": 4.2,
      "completion_rate": 0.78,
      "avg_tasks_per_agent": 6.4
    }
  },
  "generated_at": "2026-03-31T10:00:00Z"
}
```

**Response 401:** `{ "detail": "Not authenticated" }`

---

### 8.2 GET `/api/dashboard/teams`

**Descrição:** Lista todos os times do tenant com detalhes (lider, agentes, contadores).

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `status` | `string` | — | Filtrar por status: `active`, `inactive` |
| `page` | `int` | `1` | Página (1-indexed) |
| `per_page` | `int` | `20` | Itens por página (max 100) |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "backend",
      "name": "Backend",
      "emoji": "⚙️",
      "leader": {
        "id": "user-001",
        "name": "Carlos Silva",
        "role": "Tech Lead",
        "avatar": "CS"
      },
      "agents_count": 3,
      "active_tasks": 8,
      "completed_tasks": 12,
      "avg_score": 4.5,
      "status": "active"
    },
    {
      "id": "frontend",
      "name": "Frontend",
      "emoji": "🎨",
      "leader": {
        "id": "user-002",
        "name": "Ana Costa",
        "role": "Design Lead",
        "avatar": "AC"
      },
      "agents_count": 2,
      "active_tasks": 5,
      "completed_tasks": 8,
      "avg_score": 4.1,
      "status": "active"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 4,
    "pages": 1
  }
}
```

**Response 401:** `{ "detail": "Not authenticated" }`

---

### 8.3 GET `/api/dashboard/agents`

**Descrição:** Lista todos os agentes do tenant.

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `team` | `string` | — | Filtrar por team: `frontend`, `backend`, `devops`, `qa`, `design` |
| `status` | `string` | — | Filtrar por status: `online`, `busy`, `offline`, `active`, `inactive` |
| `role` | `string` | — | Filtrar por role: `executor`, `planner`, `reviewer`, `patrol` |
| `page` | `int` | `1` | Página (1-indexed) |
| `per_page` | `int` | `20` | Itens por página (max 100) |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "agent-escritor",
      "name": "AI-Escritor",
      "agent_type": "ai_escritor",
      "role": "executor",
      "team": "backend",
      "status": "online",
      "capabilities": ["backend", "api", "database"],
      "score": 4.5,
      "tasks_completed": 23,
      "tasks_rejected": 2,
      "tasks_in_progress": 3,
      "is_active": true
    },
    {
      "id": "agent-pesquisador",
      "name": "AI-Pesquisador",
      "agent_type": "ai_pesquisador",
      "role": "executor",
      "team": "backend",
      "status": "busy",
      "capabilities": ["research", "analysis"],
      "score": 4.2,
      "tasks_completed": 18,
      "tasks_rejected": 1,
      "tasks_in_progress": 1,
      "is_active": true
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 5,
    "pages": 1
  }
}
```

**Response 401:** `{ "detail": "Not authenticated" }`

---

### 8.4 GET `/api/dashboard/tasks`

**Descrição:** Lista tarefas ativas do tenant (não-cancelled, não-deleted).

**Query Parameters:**
| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `status` | `string` | — | Filtrar: `pending`, `in_progress`, `review`, `done` |
| `team` | `string` | — | Filtrar: `frontend`, `backend`, `devops`, `qa`, `design` |
| `urgency` | `string` | — | Filtrar: `high`, `medium`, `low` |
| `assignee_id` | `string` | — | Filtrar por assignee |
| `page` | `int` | `1` | Página (1-indexed) |
| `per_page` | `int` | `20` | Itens por página (max 100) |
| `sort_by` | `string` | `created_at` | Ordenar: `created_at`, `updated_at`, `urgency`, `status` |
| `sort_order` | `string` | `desc` | `asc` ou `desc` |

**Response 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "task-001",
      "title": "Implementar API de Dashboard",
      "description": "Criar endpoints REST para o dashboard",
      "status": "in_progress",
      "urgency": "high",
      "team": "backend",
      "assignee_id": "agent-escritor",
      "assignee_name": "AI-Escritor",
      "assignee_avatar": "AE",
      "parent_task_id": null,
      "has_subtasks": true,
      "subtask_count": 3,
      "created_at": "2026-03-30T09:00:00Z",
      "updated_at": "2026-03-31T08:30:00Z"
    },
    {
      "id": "task-002",
      "title": "Criar Schema do Banco",
      "description": "Modelar tabelas para agents e scores",
      "status": "review",
      "urgency": "medium",
      "team": "backend",
      "assignee_id": "agent-devops",
      "assignee_name": "AI-DevOps",
      "assignee_avatar": "AD",
      "parent_task_id": "task-001",
      "has_subtasks": false,
      "subtask_count": 0,
      "created_at": "2026-03-29T14:00:00Z",
      "updated_at": "2026-03-31T07:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 47,
    "pages": 3
  }
}
```

**Response 401:** `{ "detail": "Not authenticated" }`

---

## 9. Variáveis de Ambiente

| Variável | Valor Padrão | Descrição |
|----------|-------------|-----------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:3001` | URL base da API FastAPI (para server-side) |
| `NEXT_PUBLIC_APP_URL` | `http://localhost:3000` | URL do dashboard |
| `TELEGRAM_BOT_TOKEN` | — | Token do bot Telegram |
| `DATABASE_URL` | `sqlite:///./data/cereja.db` | Conexão do banco |
