# SPEC - Task Routing Engine
**Módulo:** Orquestrador (Orchestrator)
**Task ID:** 36f1fd0a-62d5-4f98-8620-66833b2e2fc8
**Autor:** AI-Escritor (Backend Developer)
**Data:** 2026-03-31

---

## 1. Visão Geral

O **Task Routing Engine** é o componente central do Orquestrador Cereja. Sua responsabilidade é:
1. Classificar mensagens de texto em **intents** (marketing, dev, research, design, office)
2. **Routar** a mensagem classificada para o **team** correto
3. Criar uma **subtask** no OpenMOSS para o team destinatário
4. **Notificar** o líder do time sobre a nova tarefa

---

## 2. Arquitetura

```
Usuário envia mensagem
        │
        ▼
┌─────────────────────┐
│ Intent Classifier    │  → classifica texto em intent + confidence + entities
│ (intent_classifier)  │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Task Router         │  → mapeia intent → Team, cria subtask, notifica
│ (router.py)         │
└─────────────────────┘
        │
        ▼
   Team designado
```

### 2.1 Classes Principais

| Classe | Responsabilidade | Arquivo |
|--------|-----------------|---------|
| `classify_intent(text)` | Retorna `(intent, confidence)` via keyword matching | `orchestrator/intent_classifier.py` |
| `extract_entities(text)` | Extrai entidades: `cliente_nome`, `empresa_id`, `urgencia`, `tipo_trabalho` | `orchestrator/intent_classifier.py` |
| `classify(text)` | Combina classification + extraction em `IntentResult` | `orchestrator/intent_classifier.py` |
| `Team` (Enum) | Enumera times disponíveis | `orchestrator/router.py` |
| `IntentMapping` | Mapeia intent string → Team | `orchestrator/router.py` |
| `TaskCreator` | Cria subtask (mock ou via OpenMOSS API) | `orchestrator/router.py` |
| `TeamNotifier` | Notifica líder do team (log, message, webhook) | `orchestrator/router.py` |
| `TaskRouter` | Orquestra todo o fluxo: classify → map → create → notify | `orchestrator/router.py` |

---

## 3. Intent Classification

### 3.1 Intents Suportados

| Intent | Keywords (exemplos) | Descrição |
|--------|--------------------|-----------| 
| `marketing` | campanha, seo, ads, redes sociais, branding, conteúdo, leads | Marketing e aquisição |
| `dev` | código, api, bug, app, website, deploy, github, docker, backend | Desenvolvimento |
| `research` | pesquisa, análise, relatório, dados, benchmark, métricas, KPI | Pesquisa e dados |
| `design` | ui, ux, logo, figma, branding, mockup, wireframe, layout | Design e branding |
| `office` | planilha, documento, calendário, reunião, agenda, ppt, excel | Administrativo |
| `unknown` | (sem matches) | Não classificado |

### 3.2 Algoritmo de Classificação

```python
def classify_intent(text: str) -> tuple[str, float]:
    # 1. Tokeniza texto em minúsculas
    # 2. Para cada intent, conta keywords encontradas
    # 3. Score = matches / total_keywords_para_intent  (normalização)
    # 4. Best intent = intent com maior score
    # 5. Confidence = min(score * 2, 1.0)
```

### 3.3 Extração de Entidades

| Entidade | Como é extraída | Exemplo |
|----------|-----------------|---------|
| `cliente_nome` | Regex: `cliente: Nome`, `de Nome` | "cliente: João Silva" → `cliente_nome: João Silva` |
| `empresa_id` | Regex: `empresa-XXX`, `#数字` | "empresa-001" → `empresa_id: 001` |
| `urgencia` | Keyword matching: alta/média/baixa | "urgente" → `urgencia: high` |
| `tipo_trabalho` | Priority matching: correção > atualização > criação > ... | "corrigir bug" → `tipo_trabalho: correção` |

---

## 4. Team Routing

### 4.1 Mapeamento Intent → Team

```python
INTENT_TO_TEAM = {
    "marketing":  Team.MARKETING,
    "dev":        Team.DEV,
    "development": Team.DEV,     # alias
    "research":  Team.RESEARCH,
    "design":    Team.DESIGN,
    "office":    Team.OFFICE,
}
```

### 4.2 Teams Válidos

| Team | Valor Enum | Lider (placeholder) |
|------|------------|---------------------|
| Team Dev | `Team.DEV` | Dev Leader |
| Team Marketing | `Team.MARKETING` | Marketing Leader |
| Team Research | `Team.RESEARCH` | Research Leader |
| Team Design | `Team.DESIGN` | Design Leader |
| Team Office | `Team.OFFICE` | Office Leader |
| Team Unknown | `Team.UNKNOWN` | (fallback) |

### 4.3 Fluxo de Routing

```
route(intent, entities)
  │
  ├─→ IntentMapping.get_team(intent) → Team
  │
  ├─→ TaskCreator.create_task() → task_id + status
  │     ├─ use_mock=True  → logs [MOCK] Task created
  │     └─ use_mock=False → POST /api/tasks no OpenMOSS
  │
  └─→ TeamNotifier.notify() → log / message / webhook
```

---

## 5. Task Creation

### 5.1 TaskCreator

```
Modo mock (default):
  task_data = {
    "task_id": uuid,
    "team": team.value,
    "intent": intent,
    "entities": entities,
    "status": "created",
    "created_at": ISO8601,
    "description": "..."
  }

Modo real (use_mock=False):
  POST /api/orchestrator/tasks → OpenMOSS API
```

### 5.2 Task Status Lifecycle

```
created → assigned → in_progress → review → done
                    ↘ cancelled
```

---

## 6. TeamNotifier

| Modo | Comportamento |
|------|--------------|
| `log` | Loga `[NOTIFICATION] New task assigned to Team X` |
| `message` | Placeholder para email/Slack (log + print) |
| `webhook` | Placeholder para webhook call |

---

## 7. Batch Routing

`TaskRouter.route_batch(tasks: List[Dict])` itera sobre lista de tarefas e faz routing individual para cada uma, retornando lista de resultados.

---

## 8. API Endpoints do Routing Engine

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/api/orchestrator/route` | Classifica e faz routing de mensagem |
| `POST` | `/api/orchestrator/batch` | Routing em batch |
| `POST` | `/api/orchestrator/classify` | Apenas classifica (sem routing) |
| `GET` | `/api/orchestrator/tasks/{task_id}` | Status de task por ID |
| `POST` | `/api/orchestrator/route-manual` | Routing forçado para team específico |
| `GET` | `/api/orchestrator/teams` | Status dos teams (contadores) |

---

## 9. Exemplos de Requisição/Resposta

### POST /api/orchestrator/route

**Request:**
```json
{
  "message": "Preciso criar uma campanha de marketing para o Instagram",
  "tenant_id": "tenant_001",
  "user_id": "user_abc"
}
```

**Response:**
```json
{
  "intent": "marketing",
  "confidence": 0.73,
  "team": "Team Marketing",
  "entities": {
    "tenant_id": "tenant_001",
    "user_id": "user_abc",
    "cliente_nome": null,
    "empresa_id": null,
    "urgencia": "medium",
    "tipo_trabalho": "criação",
    "raw_message": "Preciso criar uma campanha de marketing para o Instagram"
  },
  "task_id": "a1b2c3d4-...",
  "status": "created",
  "raw_text": "Preciso criar uma campanha de marketing para o Instagram"
}
```

---

## 10. Testes

Ver arquivo: `orchestrator/test_router.py` e `orchestrator/test_intent_classifier.py`

Testes cobrem:
- Classificação de intents por keywords
- Extração de entidades (urgência, tipo_trabalho, cliente_nome, empresa_id)
- Routing para team correto
- Fallback para Team.Unknown em intent desconhecido
- Batch routing
- Mock vs. real task creation
