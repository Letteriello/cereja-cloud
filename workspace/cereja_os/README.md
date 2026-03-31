# Cereja OS 🍒

**Plataforma de orquestração de agentes de IA multi-camadas.**

Cereja OS é uma plataforma que combina o **OpenClaw** (gateway de canais e agents) com o **OpenMOSS** (orquestração de tasks, review e scoring) para criar uma experiência completa de times de IA autônomos.

> **Missão:** Reduzir custos operacionais de empresas em 50% através de agentes de IA que planejam, executam, revisam e evoluem sozinhos.

---

## Índice

- [Arquitetura](#arquitetura)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura de Diretórios](#estrutura-de-diretórios)
- [Quick Start](#quick-start)
- [Deploy](#deploy)
- [API Reference](#api-reference)
- [Agentes](#agentes)

---

## Arquitetura

### Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CEREJA OS                                  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   OPENCLAW GATEWAY                          │   │
│  │              (Porta 18789 — Control Plane)                  │   │
│  │                                                              │   │
│  │  • Multi-channel (Telegram, WhatsApp, Discord, etc)         │   │
│  │  • Sessions (main + isolated por agente)                    │   │
│  │  • Skills / ClawHub marketplace                             │   │
│  │  • Cron + Webhooks                                          │   │
│  │  • WebChat integrado                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      OPENMOSS                                │   │
│  │              (Orquestração de Times)                        │   │
│  │                                                              │   │
│  │  • Agent Registry (ak_xxx API Keys)                         │   │
│  │  • Tasks + Subtasks (state machine)                         │   │
│  │  • Review System (scores 1-5)                               │   │
│  │  • Scoring (+5/-5 pontos por performance)                    │   │
│  │  • Rules (global → task → sub_task)                         │   │
│  │  • Patrol (logs de atividade)                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    CEREBRO (Cereja)                          │   │
│  │              (Orchestrator Principal)                        │   │
│  │                                                              │   │
│  │  • Planeja fluxos e workflows                               │   │
│  │  • Coordena agentes e times                                 │   │
│  │  • Decisões autônomas                                       │   │
│  │  • Supervisão e patrol                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Planning │ │  DevOps  │ │ Backend  │ │ Frontend │ │Research │  │
│  │   Team   │ │   Team   │ │   Team   │ │   Team   │ │  Team   │  │
│  │    📋    │ │    🚀    │ │    ⚙️    │ │    🎨    │ │    🔬   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │    QA    │ │ Security │ │  Office  │ │  Legal   │ │  Corp   │  │
│  │   Team   │ │   Team   │ │   Team   │ │   Team   │ │   Team  │  │
│  │    🧪    │ │    👁️    │ │    📋    │ │    ⚖️    │ │    🏢   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Camadas da Arquitetura

| Camada | Tecnologia | Função |
|--------|------------|--------|
| **Gateway** | OpenClaw | Conexão com canais (Telegram, etc), sessions, skills |
| **Orquestração** | OpenMOSS | Tasks, subtasks, review, scoring, patrol |
| **Inteligência** | Cereja | Decisões, planning, coordenação |
| **Execution** | Agentes | Executor, Pesquisador, DevOps, etc |
| **Interface** | Dashboard | Visualização, controle, métricas |

### Fluxo de Dados

```
Usuário (Telegram/WhatsApp/Web)
        │
        ▼
OpenClaw Gateway (18789)
        │
        ▼
Cereja (Orchestrator)
        │
        ├──▶ Planning Team (planner de tarefas)
        │
        ▼
OpenMOSS (cria task)
        │
        ├──▶ Executor Team (executa)
        │
        ▼
Review System (avalia)
        │
        ▼
Scoring (+5 / -5)
        │
        ▼
Patrol (logs)
```

---

## Stack Tecnológica

### Backend (API)
| Tecnologia | Uso |
|------------|-----|
| FastAPI | API Gateway |
| Python 3.11+ | Runtime |
| Uvicorn | ASGI Server |
| SQLAlchemy | ORM |
| Pydantic | Validação |
| PostgreSQL | Banco de dados |
| Redis | Cache/Sessions |

### Frontend
| Tecnologia | Uso |
|-----------|-----|
| Next.js 14 | Framework React |
| TypeScript | Tipagem |
| Tailwind CSS | Estilização |
| shadcn/ui | Componentes UI |
| Recharts | Gráficos |

### Infraestrutura
| Tecnologia | Uso |
|-----------|-----|
| Docker | Containerização |
| Nginx | Proxy reverso + SSL |
| Certbot | SSL automático |
| UFW | Firewall |

---

## Estrutura de Diretórios

```
cereja_os/
├── api/                      # Backend FastAPI (OpenMOSS)
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   ├── routers/          # API endpoints
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py           # Entry point
│   └── requirements.txt
│
├── dashboard/                # Frontend Next.js
│   ├── src/
│   │   ├── app/             # App Router
│   │   ├── components/       # React components
│   │   └── lib/             # Utils
│   └── package.json
│
├── webui/                    # Vue.js WebUI (OpenMOSS)
│   ├── src/
│   │   ├── views/           # Vue views
│   │   ├── components/       # Vue components
│   │   └── router/           # Vue Router
│   └── vite.config.ts
│
├── orchestrator/             # Cereja (Orchestrator)
│   ├── intent_classifier.py  # Classificador de intents
│   └── router.py             # Roteador de tasks
│
├── telegram/                  # Integração Telegram
│   ├── bot_main.py           # Bot entry point
│   ├── handlers.py           # Message handlers
│   └── bot_config.py         # Configuração
│
├── scripts/                   # Scripts utilitários
├── infrastructure/            # Docker, Nginx, SSL, etc
│
├── prompts/                   # Prompts dos agentes
│   ├── agents/               # Prompts por tipo
│   ├── role/                 # Papéis
│   └── templates/            # Templates
│
├── rules/                     # Regras globais
│
└── docs/                     # Documentação extra
```

---

## Quick Start

### 1. API (OpenMOSS)

```bash
cd api

# Criar venv
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Variáveis de ambiente
cp .env.example .env
# Editar .env

# Rodar migrações
alembic upgrade head

# Iniciar
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Dashboard

```bash
cd dashboard

npm install
npm run dev
```

### 3. Telegram Bot

```bash
cd telegram

# Configurar .env
cp .env.example .env

# Rodar
python bot_main.py
```

---

## Deploy

### VPS (Ubuntu)

```bash
# Setup inicial
chmod +x infrastructure/vps-setup.sh
sudo ./infrastructure/vps-setup.sh

# Firewall
chmod +x infrastructure/ufw-firewall.sh
sudo ./infrastructure/ufw-firewall.sh

# SSL
chmod +x infrastructure/ssl-setup.sh
sudo ./infrastructure/ssl-setup.sh

# Docker
cd infrastructure/docker
docker-compose -f docker-compose.prod.yml up -d
```

### URLs em Produção

| Serviço | URL |
|---------|-----|
| Dashboard | https://cereja.cloud |
| API | https://cereja.cloud/api |
| Telegram | @seu_bot |
| WebChat | https://cereja.cloud/chat |

---

## API Reference

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/agents` | Lista todos os agentes |
| GET | `/api/agents/{id}` | Detalhes de um agente |
| GET | `/api/tasks` | Lista tasks |
| POST | `/api/tasks` | Cria nova task |
| PATCH | `/api/tasks/{id}` | Atualiza task |
| GET | `/api/scores` | Scores dos agentes |
| GET | `/api/rules` | Regras ativas |
| GET | `/api/patrol` | Logs de patrol |

### Autenticação

```bash
# Header padrão
Authorization: Bearer <api_key>
```

---

## Agentes

### Papéis (OpenMOSS)

| Role | Função |
|------|--------|
| **planner** | Planeja tarefas e divide em subtasks |
| **executor** | Executa tarefas atribuídas |
| **reviewer** | Revisa e avalia resultados |
| **patrol** | Monitora e faz audit logs |

### Times Padrão

| Time | Agentes |
|------|---------|
| **Planning** | Planejador, Analista |
| **DevOps** | DevOps, Infra |
| **Backend** | Escritor, DB Admin |
| **Frontend** | Publicador, UI/UX |
| **Research** | Pesquisador, Analista |
| **QA** | Testador |
| **Security** | Patrulheiro |

### Sistema de Scoring

| Avaliação | Pontos |
|-----------|--------|
| Nota 4-5 (bom) | +5 pontos |
| Nota 3 (médio) | 0 pontos |
| Nota 1-2 (ruim) | -5 pontos |

---

## Diferenciais do Cereja OS

### 1. Agentes Autônomos
- Work 24/7 sem intervenção humana
- Aprendem com revisões (scoring)
- Se auto-melhoram com skills

### 2. Times Hierárquicos
- Cereja como orchestrator principal
- Team leaders delegam para specialists
- Supervisão inteligente

### 3. Multi-Channel
- Telegram, WhatsApp, Discord, Web
- Tudo conectado no mesmo sistema
- Uma resposta, múltiplos canais

### 4. Revisão e Scoring
- Toda tarefa é revisada
- Scores afetam performance
- Evolução contínua

### 5. Regras Configuráveis
- Global → Task → Sub-task
- Variáveis substituíveis
- Flexível por contexto

---

## Roadmap

### Fase 1 ✅
- [x] OpenClaw Gateway (Telegram, WebChat)
- [x] OpenMOSS (Tasks, Review, Scoring)
- [x] Dashboard básico
- [x] API integrada

### Fase 2 (Em Progresso)
- [ ] Memory persistente por agente
- [ ] Skills auto-improving
- [ ] Interface visual de times

### Fase 3
- [ ] Marketplace de agentes
- [ ] Templates por vertical
- [ ] Multi-tenant completo

---

## Links

- **Frontend:** https://cereja.cloud
- **API:** https://cereja.cloud/api
- **Docs:** https://github.com/Letteriello/cereja-cloud

---

_Built with 🍒 by Gabriel Letteriello_

**OpenClaw** — Gateway e canais  
**OpenMOSS** — Orquestração e tasks  
**Cereja** — Inteligência e coordenação
