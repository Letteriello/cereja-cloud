"""
Unit tests for Intent Classification Module
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intent_classifier import classify, classify_intent, extract_entities, IntentResult


class TestIntentClassification(unittest.TestCase):
    """Test cases for intent classification."""

    def test_marketing_intent(self):
        """Test marketing intent classification."""
        test_cases = [
            "Preciso criar uma campanha de marketing para o Instagram",
            "Quero fazer copy para Facebook ads",
            "Preciso de estratégia SEO para meu site",
            "Criar post para redes sociais",
            "Campanha de anúncios no Google",
        ]
        for text in test_cases:
            intent, confidence = classify_intent(text)
            self.assertEqual(intent, "marketing", f"Failed for: {text}")
            self.assertGreater(confidence, 0.0)

    def test_dev_intent(self):
        """Test dev intent classification."""
        test_cases = [
            "Preciso corrigir um bug no meu app",
            "Desenvolver uma API REST",
            "Criar um website novo",
            "Deploy do projeto no servidor",
            "Corrigir erro no código Python",
        ]
        for text in test_cases:
            intent, confidence = classify_intent(text)
            self.assertEqual(intent, "dev", f"Failed for: {text}")
            self.assertGreater(confidence, 0.0)

    def test_research_intent(self):
        """Test research intent classification."""
        test_cases = [
            "Preciso de uma análise de dados do mercado",
            "Fazer pesquisa sobre concorrentes",
            "Relatório de métricas do site",
            "Estudo de tendência do setor",
            "Levantamento de informações",
        ]
        for text in test_cases:
            intent, confidence = classify_intent(text)
            self.assertEqual(intent, "research", f"Failed for: {text}")
            self.assertGreater(confidence, 0.0)

    def test_design_intent(self):
        """Test design intent classification."""
        test_cases = [
            "Preciso criar um logo para minha empresa",
            "Fazer identidade visual",
            "Design de UI para o app",
            "Criar mockup de banner",
            "Mockup do protótipo",
        ]
        for text in test_cases:
            intent, confidence = classify_intent(text)
            self.assertEqual(intent, "design", f"Failed for: {text}")
            self.assertGreater(confidence, 0.0)

    def test_office_intent(self):
        """Test office intent classification."""
        test_cases = [
            "Preciso organizar planilhas de vendas",
            "Criar documento no Google Docs",
            "Agendar reunião para semana",
            "Preciso fazer uma apresentação PowerPoint",
            "Editar texto no Word",
        ]
        for text in test_cases:
            intent, confidence = classify_intent(text)
            self.assertEqual(intent, "office", f"Failed for: {text}")
            self.assertGreater(confidence, 0.0)


class TestEntityExtraction(unittest.TestCase):
    """Test cases for entity extraction."""

    def test_urgency_high(self):
        """Test high urgency extraction."""
        texts = [
            "Preciso urgente corrigir o bug",
            "É emergência, precisa agora ASAP",
            "Trabalho crítico para hoje",
        ]
        for text in texts:
            entities = extract_entities(text)
            self.assertEqual(entities["urgencia"], "high", f"Failed for: {text}")

    def test_urgency_low(self):
        """Test low urgency extraction."""
        texts = [
            "Quero fazer quando puder",
            "Sem pressa, pode ser no futuro",
            "Tarefa sem urgência",
        ]
        for text in texts:
            entities = extract_entities(text)
            self.assertEqual(entities["urgencia"], "low", f"Failed for: {text}")

    def test_urgency_medium(self):
        """Test medium urgency extraction (default)."""
        texts = [
            "Preciso resolver isso",
            "Algo normal",
            "Tarefa comum",
        ]
        for text in texts:
            entities = extract_entities(text)
            self.assertEqual(entities["urgencia"], "medium", f"Failed for: {text}")

    def test_work_type_criacao(self):
        """Test criação work type extraction."""
        text = "Preciso criar um novo website"
        entities = extract_entities(text)
        self.assertEqual(entities["tipo_trabalho"], "criação")

    def test_work_type_correcao(self):
        """Test correção work type extraction."""
        text = "Corrigir bug no sistema"
        entities = extract_entities(text)
        self.assertEqual(entities["tipo_trabalho"], "correção")

    def test_work_type_atualizacao(self):
        """Test atualização work type extraction."""
        text = "Atualizar o app para nova versão"
        entities = extract_entities(text)
        self.assertEqual(entities["tipo_trabalho"], "atualização")

    def test_empresa_id_extraction(self):
        """Test empresa_id extraction."""
        texts = [
            ("Cliente: empresa-123", "123"),
            ("empresa_id: ABC123", "ABC123"),
            ("emp-XYZ789", "XYZ789"),
            ("ID: #42", "42"),
        ]
        for text, expected in texts:
            entities = extract_entities(text)
            self.assertEqual(entities["empresa_id"], expected, f"Failed for: {text}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_empty_input(self):
        """Test empty input returns unknown intent."""
        result = classify("")
        self.assertEqual(result.intent, "unknown")
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.entities["urgencia"], "medium")

    def test_whitespace_only(self):
        """Test whitespace-only input."""
        result = classify("   ")
        self.assertEqual(result.intent, "unknown")
        self.assertEqual(result.confidence, 0.0)

    def test_none_input(self):
        """Test None input handling."""
        result = classify(None)
        self.assertEqual(result.intent, "unknown")
        self.assertEqual(result.confidence, 0.0)

    def test_invalid_unknown_text(self):
        """Test text with no matching keywords."""
        result = classify("xyz abc 123")
        self.assertEqual(result.intent, "unknown")
        self.assertEqual(result.confidence, 0.0)

    def test_intent_result_dataclass(self):
        """Test IntentResult contains all required fields."""
        result = classify("Preciso criar uma campanha de marketing")
        self.assertIsInstance(result, IntentResult)
        self.assertIn("intent", result.__dict__)
        self.assertIn("confidence", result.__dict__)
        self.assertIn("entities", result.__dict__)
        self.assertIn("raw_text", result.__dict__)

    def test_raw_text_preserved(self):
        """Test raw text is preserved in result."""
        original = "Preciso criar uma campanha de marketing"
        result = classify(original)
        self.assertEqual(result.raw_text, original)

    def test_confidence_range(self):
        """Test confidence is between 0 and 1."""
        texts = [
            "Preciso criar uma campanha de marketing para o Instagram",
            "Desenvolver API REST",
            "Bug no app",
        ]
        for text in texts:
            result = classify(text)
            self.assertGreaterEqual(result.confidence, 0.0)
            self.assertLessEqual(result.confidence, 1.0)

    def test_entities_keys(self):
        """Test all required entity keys exist."""
        result = classify("Test input")
        self.assertIn("cliente_nome", result.entities)
        self.assertIn("empresa_id", result.entities)
        self.assertIn("urgencia", result.entities)
        self.assertIn("tipo_trabalho", result.entities)


class TestFullPipeline(unittest.TestCase):
    """Test full classification pipeline."""

    def test_full_pipeline_marketing(self):
        """Test complete pipeline for marketing intent."""
        text = "Urgente! Preciso criar uma campanha de marketing para Instagram da empresa-999"
        result = classify(text)
        self.assertEqual(result.intent, "marketing")
        self.assertGreater(result.confidence, 0.0)
        self.assertEqual(result.entities["urgencia"], "high")
        self.assertEqual(result.entities["empresa_id"], "999")

    def test_full_pipeline_dev(self):
        """Test complete pipeline for dev intent."""
        text = "Bug crítico no app - empresa-123"
        result = classify(text)
        self.assertEqual(result.intent, "dev")
        self.assertGreater(result.confidence, 0.0)
        self.assertEqual(result.entities["urgencia"], "high")
        self.assertEqual(result.entities["empresa_id"], "123")
        self.assertEqual(result.entities["tipo_trabalho"], "correção")

    def test_full_pipeline_office(self):
        """Test complete pipeline for office intent."""
        text = "Preciso organizar planilhas de vendas da empresa-456"
        result = classify(text)
        self.assertEqual(result.intent, "office")
        self.assertGreater(result.confidence, 0.0)
        self.assertEqual(result.entities["empresa_id"], "456")


if __name__ == "__main__":
    unittest.main()
