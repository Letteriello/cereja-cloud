"""
Intent Classification Module for Cereja OS
Classifies customer text input into intent categories and extracts entities.
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class IntentResult:
    """Result of intent classification."""
    intent: str
    confidence: float
    entities: dict
    raw_text: str


# Keywords for each intent category
INTENT_KEYWORDS = {
    "marketing": [
        "campanha", "campanhas", "copy", "social media", "redes sociais",
        "seo", "ads", "anúncio", "anuncios", "facebook", "instagram",
        "google ads", "marketing", "branding", "Conteúdo", "conteudo",
        "publicidade", "promoção", "promocao", "email marketing",
        "landing page", "funil", "leads", "tráfego", "trafego"
    ],
    "dev": [
        "código", "codigo", "api", "bug", "app", "website", "site",
        "desenvolvimento", "dev", "programar", "programação", "programacao",
        "backend", "frontend", "fullstack", "database", "banco de dados",
        "servidor", "deploy", "github", "docker", "container", "microserviço",
        "microservico", "rest", "graphql", "python", "javascript", "java",
        "react", "node", "vue", "angular", "sql", "nosql", "cloud", "aws",
        "azure", "gcp", "crash", "erro", "falha", "não funciona",
        "nao funciona", "corrigir", "corrige", "corrigir bug", "construir"
    ],
    "research": [
        "pesquisa", "análise", "analise", "relatório", "relatorio", "dados",
        "estudo", "investigação", "investigacao", "levantamento", "benchmark",
        "comparar", "comparativo", "métricas", "metricas", "kpi", "dashboard",
        "analytics", "relatório", "dados", "inteligência", "inteligencia",
        "mercado", "concorrente", "concorrentes", "tendência", "tendencia"
    ],
    "design": [
        "ui", "ux", "logo", "branding", "imagem", "design", "figma",
        "photoshop", "ilustração", "ilustracao", "banner", "cartão", "cartao",
        "cartaz", "flyer", "identidade visual", "mockup", "protótipo",
        "prototipo", "wireframe", "layout", "tipografia", "cores", "paleta",
        "icon", "ícone", "icone", "ilustração", "ilustracao", "arte"
    ],
    "office": [
        "planilha", "spreadsheet", "docs", "documento", "documentos",
        "calendário", "calendario", "organização", "organizacao", "ppt",
        "powerpoint", "excel", "word", "google docs", "google sheets",
        "reunião", "reuniao", "agenda", "tarefa", "tarefas", "notas",
        "relatório", "relatorio", "texto", "editar", "formatação",
        "formatacao", "tabela", "gráfico", "grafico", "pasta", "arquivo"
    ]
}

# Urgency indicators
URGENCY_HIGH = ["urgente", "urgência", "urgencia", "emergency", " ASAP", "agora", "já", "ja", "immediately", "crítico", "critico", "hoje"]
URGENCY_MEDIUM = ["breve", "logo", "semana", "essa semana", "próximo", "proximo", "preferencialmente", " depressa"]
URGENCY_LOW = ["quando puder", "sem pressa", "devagar", "sem urgência", "sem urgencia", "futuro", "later"]

# Work type indicators (used via work_type_priority in extract_entities)


def classify_intent(text: str) -> tuple[str, float]:
    """
    Classify text into one of the intent categories.
    Returns (intent, confidence) tuple.
    """
    if not text or not text.strip():
        return "unknown", 0.0

    text_lower = text.lower()
    scores: dict[str, float] = {}

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0.0
        matched_keywords = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += 1.0
                matched_keywords += 1
        if matched_keywords > 0:
            # Normalize by number of keywords to avoid bias
            scores[intent] = score / len(keywords)

    if not scores:
        return "unknown", 0.0

    # Get the intent with highest score
    best_intent = max(scores, key=scores.get)
    best_score = scores[best_intent]

    # Normalize confidence to 0-1 range
    confidence = min(best_score * 2, 1.0) if best_score > 0 else 0.0

    return best_intent, confidence


def extract_entities(text: str) -> dict:
    """
    Extract entities from text: cliente_nome, empresa_id, urgencia, tipo_trabalho.
    """
    entities = {
        "cliente_nome": None,
        "empresa_id": None,
        "urgencia": "medium",
        "tipo_trabalho": None
    }

    if not text:
        return entities

    text_lower = text.lower()

    # Extract urgency - check for negation first
    urgency_text = text_lower
    # Check for negation patterns first
    has_no_urgency = bool(re.search(r'sem\s+(?:urgência|urgencia|press[aã]o)', urgency_text))
    
    if has_no_urgency:
        entities["urgencia"] = "low"
    elif any(kw in urgency_text for kw in URGENCY_HIGH):
        entities["urgencia"] = "high"
    elif any(kw in urgency_text for kw in URGENCY_LOW):
        entities["urgencia"] = "low"
    else:
        entities["urgencia"] = "medium"

    # Extract work type - more specific matches first
    work_type_priority = [
        ("correção", ["corrigir", "correção", "correcao", "fix", "arrumar", "bug", "erro", "falha", "problema"]),
        ("atualização", ["atualizar", "atualização", "atualizacao", "update", "upgrade"]),
        ("criação", ["criar", "criação", "criacao", "novo", "nova", "build", "construir"]),
        ("consultoria", ["consultar", "consultoria", "advise", "orientar", "orientação", "orientacao", "help", "ajuda"]),
        ("manutenção", ["manutenção", "manutencao", "maintenance", "suporte", "support", "assistência", "assistencia"]),
    ]
    
    for work_type, keywords in work_type_priority:
        if any(kw in text_lower for kw in keywords):
            entities["tipo_trabalho"] = work_type
            break

    # Extract empresa_id (pattern: empresa-XXX, emp-XXX, company-XXX, or numeric IDs)
    empresa_patterns = [
        r'(?:empresa_id|empresaid|cliente_id|clienteid)[\s:]?\s*(\w+)',
        r'(?:cliente)[\s:]+(?:empresa[\s_-])?(\w+)',
        r'(?:\b(?:empresa|company))(?:[\s_-](\w+))?',
        r'(?<![a-z])emp(?:[\s_-](\w+))?',
        r'#(\d+)',
    ]
    for pattern in empresa_patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Capture group 1 contains the ID if available
            if match.lastindex and match.lastindex >= 1:
                entities["empresa_id"] = match.group(1).upper()
            break

    # Extract cliente_nome (look for patterns like "cliente: Nome" or "cliente Nome")
    cliente_patterns = [
        r'(?:cliente|nome|cliente_nome|nome_do_cliente)[\s:]+([A-Za-z\s]+?)(?:\s|,|$)',
        r'(?:para|att|atendimento)\s+([A-Za-z\s]+?)(?:\s|,|$)',
        r'^(?:de|from)\s+([A-Za-z\s]+?)(?:\s|,|$)',
    ]
    for pattern in cliente_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nome = match.group(1).strip()
            if len(nome) > 1 and len(nome) < 50:
                entities["cliente_nome"] = nome.title()
                break

    return entities


def classify(text: str) -> IntentResult:
    """
    Main classification function.
    Receives customer text input and returns IntentResult.
    """
    intent, confidence = classify_intent(text)
    entities = extract_entities(text)

    return IntentResult(
        intent=intent,
        confidence=confidence,
        entities=entities,
        raw_text=text
    )


if __name__ == "__main__":
    # Demo usage
    test_texts = [
        "Preciso criar uma campanha de marketing para o Instagram",
        "Meu app está com bug, precisa corrigir urgente",
        "Preciso de uma análise de dados do mercado",
        "Quero um logo novo para minha empresa",
        "Preciso organizar planilhas de vendas"
    ]

    for text in test_texts:
        result = classify(text)
        print(f"Text: {text}")
        print(f"  Intent: {result.intent} (confidence: {result.confidence:.2f})")
        print(f"  Entities: {result.entities}")
        print()
