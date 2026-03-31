# Cereja OS — Research Consolidation: Agent Technologies & Integrations

**Data:** 2026-03-31
**Consolidado por:** AI-Pesquisador
**Projeto:** Cereja OS (ID: 09f1041f-718c-40c3-8595-281a0750ddaa)

---

## Research Status

| Tecnologia | Status | Arquivo |
|-----------|--------|---------|
| Agent Zero | ✅ Done | research_agent_zero.md |
| Hermes AI | ✅ Done | (pesquisa previa) |
| Nemo Cloud | ✅ Done | (pesquisa previa) |
| Enxames Agentes (crewAI/AutoGen/LangGraph) | ✅ Done | research_agent_swarms.md |
| Google Workspace (Sheets/Calendar/Docs) | ✅ Done | (pesquisa previa) |
| Knowledge Base Best Practices 2026 | ✅ Done | research/KB_BEST_PRACTICES_2026.md |
| WhatsApp Business API 2026 | ✅ Done | research/WHATSAPP_API_2026.md |

---

## Agent Zero (github.com/reflex脑子/agent-zero)

### O que é
Framework de agente AI com memória persistente e capacidade de uso de ferramentas. Arquitetura baseada em "agentic loops" onde o agente pode decidir dinamicamente quais ferramentas chamar.

### Diferenciais para Cereja OS
- Memória persistente entre sessões (importante para contexto de empresa)
- Suporte a ferramentas customizadas via plugin system
- Código aberto ativo no GitHub

### Status no Mercado
- Comunidade crescente, documentação em expansão
- Adequado para prototipagem e 연구

---

## Hermes AI

### O que é
Plataforma de agentes AI focada em orquestração enterprise. Oferece agentes pré-configurados para casos de uso comuns.

### Oportunidade para Cereja OS
- Modelos de agente podem servir como referência/inspiração para especialização Cereja
- Arquitetura de orquestração enterprise pode informar desenho do orchestrator Cereja

---

## Nemo Cloud

### O que é
Plataforma cloud de agentes AI com foco em automação de workflows empresariais.

### Comparativo com OpenClaw/Cereja OS
- Nemo Cloud: solução SaaS proprietária
- Cereja OS: open-core, auto-hospedável (diferencial para mercado SMB que quer controle de dados)

---

## Enxames de Agentes — crewAI, AutoGen, LangGraph

### crewAI
- Framework demulti-agent orchestration
- Agentes com roles e goals definidos
- **Bom para:** workflows paralelos com especialização
- LangChain nativo

### AutoGen (Microsoft)
- Conversational agents que colaboram
- Customizable backends (OpenAI, Azure, local)
- Human-in-the-loop nativo
- **Bom para:** cenários que exigem revisão humana

### LangGraph
- Graph-based agent orchestration
- Estado compartilhado entre agentes
- Ciclo de feedback estruturado
- **Bom para:** workflows complexos com estados e transições definidas

### Recomendação Cereja OS
- **LangGraph** como base de orquestração (mais flexível, open source, integrado com LangChain)
- **crewAI** para padrões de role-based agents
- Inspiração do **AutoGen** para human-in-the-loop

---

## Google Workspace Integrations

### Sheets
- API Google Sheets para leitura/escrita de dados tabulares
- Cenários: relatórios de métricas, export de dados de tasks
- Autenticação via OAuth2

### Calendar
- Google Calendar API para gestão de eventos/reuniões
- Possível usar para scheduling automático de tarefas
- Webhook para notifications

### Docs
- Google Docs API para geração automática de documentação
- Gerar relatórios, KB articles automaticamente

### Recomendação Cereja OS
- MVP: não prioritário — focar em core WhatsApp + KB
- Fase 2: integração Sheets para dashboards/export
- Fase 3: Calendar para scheduling de tarefas

---

## Knowledge Base — Recomendações Consolidadas

### Arquitetura Recomendada
- **Hybrid Search** (vector + lexical) — melhor dos dois mundos
- Stack: Qdrant (vector) + Elasticsearch (fallback lexical)
- Embeddings: sentence-transformers (gratuito, self-hosted)

### KPIs Alvo
- Deflection Rate: 40–50%
- Cost per interaction: US$0.70–0.90
- CSAT: >85%

---

## WhatsApp Business API — Recomendações Consolidadas

### 2026 Changes Críticas
- **100K/day baseline** (tiers 2K/10K removidos)
- **Portfolio Pacing** — mensagens liberadas em lotes com feedback check
- **BSUID** (Q2 2026) — novos identificadores de usuário

### Provedor Recomendado
- MVP: Cloud API direto (menor custo)
- Scale-out Brasil: Wati ou Klabot (suporte PT-BR)

### Arquitetura Webhook
- Idempotência via message_id
- Async processing
- Exponential backoff

---

## Próximos Passos Recomendados

1. **Prioridade Alta:** Finalizar onboarding de agentes WhatsApp (MVP do mercado)
2. **Prioridade Alta:** Implementar KB com Hybrid Search (diferencial competitivo)
3. **Prioridade Média:** Adotar LangGraph para orquestração de agentes
4. **Prioridade Média:** Preparar migração BSUID no data model
5. **Prioridade Baixa:** Google Workspace integrations (Fase 2+)

---

## Fontes

- research_agent_zero.md (cereja_os)
- research_agent_swarms.md (cereja_os)
- KB_BEST_PRACTICES_2026.md (cereja_os/research/)
- WHATSAPP_API_2026.md (cereja_os/research/)
- ZenML — Vector Databases for RAG (2026)
- Wonderchat — RAG Benchmark Report 2026
- LinkedIn — WhatsApp Business API 2026 Updates
- Respond.io — WhatsApp API Providers 2026
