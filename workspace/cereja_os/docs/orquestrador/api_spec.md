# SPEC - Orquestrador API Endpoints
**Módulo:** Orquestrador (Orchestrator)
**Task ID:** 361913d3-8443-4ad5-a8c0-1ad399c3a902
**Autor:** AI-Escritor (Backend Developer)
**Data:** 2026-03-31

---

## 1. Visão Geral

API REST do Orquestrador Cereja OS. Endpoints para criar, rotear, consultar e gerenciar tasks e teams.

**Base URL:** `/api/orchestrator`
**Versão API:** 1.0
**Prefix global:** `/api` (via `settings.API_V1_PREFIX`)

---

## 2. Endpoints

### 2.1 POST `/api/orchestrator/route`

**Resumo:** Classifica mensagem e faz routing para o team correto.

**Tags:** orchestrator

**Request Body:**
```json
{
  "message": "string (required, 1-2000 chars) — Texto do usuário",
  "tenant_id": "string (required) — ID do tenant/empresa",
  "user_id": "string (required) — ID do usuário"
}
```

**Response 200:**
```json
{
  "intent": "string — Intent classificado (marketing|dev|research|design|office|unknown)",
  "confidence": "float (0.0-1.0) — Confiança da classificação",
  "team": "string — Team designado (Team Dev|Team Marketing|Team Research|Team Design|Team Office|Team Unknown)",
  "entities": {
    "tenant_id": "string",
    "user_id": "string",
    "cliente_nome": "string|null",
    "empresa_id": "string|null",
    "urgencia": "string (high|medium|low)",
    "tipo_trabalho": "string|null (correção|atualização|criação|consultoria|manutenção|null)",
    "raw_message": "string"
  },
  "task_id": "string (UUID) — ID da task criada",
  "status": "string — Sempre 'created' neste endpoint",
  "raw_text": "string — Texto original da mensagem"
}
```

**Response 400:** `{"detail": "Erro de validação ou intent vazio"}`
**Response 503:** `{"detail": "Orchestrator module not available"}`
**Response 500:** `{"detail": "Failed to route message"}`

**Exemplo curl:**
```bash
curl -X POST https://cereja.cloud/api/orchestrator/route \
  -H "Content-Type: application/json" \
  -d '{"message":"Preciso corrigir um bug no app","tenant_id":"emp_001","user_id":"user_123"}'
```

---

### 2.2 GET `/api/orchestrator/tasks/{task_id}`

**Resumo:** Retorna o status de uma task criada via `/route`.

**Tags:** orchestrator

**Path Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `task_id` | string (UUID) | ID da task retornado pelo `/route` |

**Response 200:**
```json
{
  "task_id": "string",
  "team": "string",
  "intent": "string",
  "status": "string (created|assigned|in_progress|review|done|cancelled)",
  "entities": {},
  "created_at": "string (ISO8601)",
  "description": "string|null"
}
```

**Response 404:** `{"detail": "Task not found"}`

---

### 2.3 POST `/api/orchestrator/route-manual`

**Resumo:** Força routing para um team específico, ignorando classificação automática.

**Tags:** orchestrator

**Request Body:**
```json
{
  "message": "string (required, 1-2000 chars)",
  "tenant_id": "string (required)",
  "user_id": "string (required)",
  "override_team": "string (required) — Team Dev|Team Marketing|Team Research|Team Design|Team Office",
  "urgency": "string (optional, default: medium) — high|medium|low",
  "description": "string (optional) — Descrição customizada da task"
}
```

**Response 200:**
```json
{
  "intent": "manual_override",
  "confidence": 1.0,
  "team": "string — Team espeficado em override_team",
  "entities": {
    "tenant_id": "string",
    "user_id": "string",
    "urgencia": "string",
    "raw_message": "string",
    "override": true
  },
  "task_id": "string (UUID)",
  "status": "created",
  "raw_text": "string"
}
```

**Response 400:** `{"detail": "Invalid team 'X'. Must be one of: Team Dev, Team Design..."}`
**Response 400:** `{"detail": "Invalid urgency 'X'. Must be one of: high, medium, low"}`

---

### 2.4 GET `/api/orchestrator/teams`

**Resumo:** Retorna contadores de tasks (total, pending, in_progress, done_last_24h) por team para um tenant.

**Tags:** orchestrator

**Query Parameters:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `tenant_id` | string (required) | ID do tenant |

**Response 200:**
```json
{
  "tenant_id": "string",
  "teams": [
    {
      "name": "Team Design",
      "tasks_total": 10,
      "tasks_pending": 3,
      "tasks_in_progress": 2,
      "tasks_done_last_24h": 5
    },
    {
      "name": "Team Dev",
      "tasks_total": 7,
      "tasks_pending": 1,
      "tasks_in_progress": 4,
      "tasks_done_last_24h": 2
    }
  ],
  "generated_at": "string (ISO8601)"
}
```

---

### 2.5 POST `/api/orchestrator/classify`

**Resumo:** Classifica intent sem criar task (útil para debug/teste).

**Tags:** orchestrator

**Request Body:**
```json
{
  "message": "string (required, 1-2000 chars)"
}
```

**Response 200:**
```json
{
  "intent": "string",
  "confidence": 0.73,
  "entities": {
    "cliente_nome": null,
    "empresa_id": null,
    "urgencia": "medium",
    "tipo_trabalho": "criação"
  },
  "raw_text": "string — Texto original"
}
```

**Response 503:** `{"detail": "Orchestrator module not available"}`
**Response 500:** `{"detail": "Failed to classify message"}`

---

### 2.6 POST `/api/orchestrator/batch`

**Resumo:** Routing em lote para múltiplas mensagens.

**Tags:** orchestrator

**Request Body:**
```json
{
  "messages": [
    {
      "message": "string (required)",
      "tenant_id": "string (optional, default: 'unknown')",
      "user_id": "string (optional, default: 'unknown')"
    }
  ]
}
```

**Response 200:**
```json
{
  "results": [
    {
      "intent": "string",
      "confidence": 0.7,
      "team": "string",
      "entities": {},
      "task_id": "string",
      "status": "created",
      "raw_text": "string"
    }
  ],
  "total": 3
}
```

---

## 3. Códigos de Erro

| HTTP Status | Significado |
|-------------|-------------|
| 200 | Sucesso |
| 400 | Erro de validação (parâmetros inválidos) |
| 404 | Recurso não encontrado (task_id inexistente) |
| 405 | Método não permitido |
| 500 | Erro interno do servidor |
| 503 | Módulo do orquestrador não disponível (import error) |

---

## 4. Auth / Headers

Os endpoints não possuem autenticação explícita no spec atual. O `tenant_id` e `user_id` são passados no body/query como identificadores.

Headers recomendados:
```
Content-Type: application/json
Accept: application/json
```

---

## 5. Schemas Pydantic (código fonte)

Ver: `cereja_os/api/app/api/orchestrator.py`

| Schema | Uso |
|--------|-----|
| `RouteRequest` | POST /route |
| `RouteResponse` | Resposta de /route |
| `ClassifyRequest` | POST /classify |
| `ClassifyResponse` | Resposta de /classify |
| `RouteManualRequest` | POST /route-manual |
| `RouteResponse` | Resposta de /route-manual |
| `TaskStatusResponse` | GET /tasks/{task_id} |
| `TeamsResponse` | GET /teams |
| `TeamStatusItem` | Item dentro de TeamsResponse |
| `BatchRouteRequest` | POST /batch |
| `BatchRouteResponse` | Resposta de /batch |

---

## 6. Mock vs. Real

- Por default, `TaskRouter(use_mock_tasks=True)` — tasks são criadas em memória
- Para usar OpenMOSS real API, definir `use_mock_tasks=False` e fornecer `api_url`
- Configuração via variável de ambiente ou `settings.py`

---

## 7. Registro no FastAPI (main.py)

```python
from app.api.orchestrator import router as orchestrator_router

app.include_router(orchestrator_router, prefix=settings.API_V1_PREFIX)
# → /api/orchestrator/*
```

Router registrado em: `cereja_os/api/app/main.py`
