"""
Unit Tests for Task Router - ST 2.2
Cereja OS Orchestrator

Tests routing logic, task creation, and edge cases.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from router import (
    TaskRouter,
    Team,
    IntentMapping,
    TaskCreator,
    TeamNotifier,
    route_task,
)


class TestIntentMapping(unittest.TestCase):
    """Test intent-to-team mapping logic."""
    
    def test_marketing_intent(self):
        """Test marketing intent routes to Team Marketing."""
        self.assertEqual(IntentMapping.get_team("marketing"), Team.MARKETING)
        self.assertEqual(IntentMapping.get_team("MARKETING"), Team.MARKETING)
        self.assertEqual(IntentMapping.get_team("  marketing  "), Team.MARKETING)
    
    def test_dev_intent(self):
        """Test dev intent routes to Team Dev."""
        self.assertEqual(IntentMapping.get_team("dev"), Team.DEV)
        self.assertEqual(IntentMapping.get_team("DEV"), Team.DEV)
        self.assertEqual(IntentMapping.get_team("development"), Team.DEV)
    
    def test_research_intent(self):
        """Test research intent routes to Team Research."""
        self.assertEqual(IntentMapping.get_team("research"), Team.RESEARCH)
        self.assertEqual(IntentMapping.get_team("RESEARCH"), Team.RESEARCH)
    
    def test_design_intent(self):
        """Test design intent routes to Team Design."""
        self.assertEqual(IntentMapping.get_team("design"), Team.DESIGN)
        self.assertEqual(IntentMapping.get_team("DESIGN"), Team.DESIGN)
    
    def test_office_intent(self):
        """Test office intent routes to Team Office."""
        self.assertEqual(IntentMapping.get_team("office"), Team.OFFICE)
        self.assertEqual(IntentMapping.get_team("OFFICE"), Team.OFFICE)
    
    def test_unknown_intent(self):
        """Test unknown intent routes to Team Unknown."""
        self.assertEqual(IntentMapping.get_team("unknown"), Team.UNKNOWN)
        self.assertEqual(IntentMapping.get_team("random"), Team.UNKNOWN)
        self.assertEqual(IntentMapping.get_team(""), Team.UNKNOWN)
        self.assertEqual(IntentMapping.get_team("  "), Team.UNKNOWN)


class TestTaskCreator(unittest.TestCase):
    """Test task creation logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.creator = TaskCreator(use_mock=True)
    
    def test_create_task_returns_valid_structure(self):
        """Test that create_task returns expected keys."""
        result = self.creator.create_task(
            intent="marketing",
            entities={"campaign": "summer_sale"},
            team=Team.MARKETING
        )
        
        self.assertIn("task_id", result)
        self.assertIn("team", result)
        self.assertIn("intent", result)
        self.assertIn("entities", result)
        self.assertIn("status", result)
        self.assertIn("created_at", result)
    
    def test_create_task_generates_uuid(self):
        """Test that task_id is a valid UUID."""
        result = self.creator.create_task(
            intent="dev",
            entities={},
            team=Team.DEV
        )
        
        # Verify UUID format
        self.assertEqual(len(result["task_id"]), 36)
        self.assertEqual(result["task_id"].count("-"), 4)
    
    def test_create_task_status_is_created(self):
        """Test that status is 'created'."""
        result = self.creator.create_task(
            intent="research",
            entities={},
            team=Team.RESEARCH
        )
        
        self.assertEqual(result["status"], "created")
    
    def test_create_task_with_description(self):
        """Test task creation with custom description."""
        description = "Build a new feature"
        result = self.creator.create_task(
            intent="dev",
            entities={},
            team=Team.DEV,
            description=description
        )
        
        self.assertEqual(result["description"], description)


class TestTeamNotifier(unittest.TestCase):
    """Test team notification logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.notifier = TeamNotifier(notification_mode="log")
    
    def test_notify_returns_true(self):
        """Test that notify returns True on success."""
        result = self.notifier.notify(
            task_id="test-123",
            team=Team.MARKETING,
            intent="marketing",
            entities={}
        )
        
        self.assertTrue(result)
    
    def test_notify_with_all_modes(self):
        """Test notify works with all notification modes."""
        for mode in ["log", "message", "webhook"]:
            notifier = TeamNotifier(notification_mode=mode)
            result = notifier.notify(
                task_id="test-456",
                team=Team.DEV,
                intent="dev",
                entities={"feature": "api"}
            )
            self.assertTrue(result)


class TestTaskRouter(unittest.TestCase):
    """Test main TaskRouter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.router = TaskRouter(use_mock_tasks=True)
    
    def test_route_marketing(self):
        """Test routing marketing intent to Team Marketing."""
        result = self.router.route(intent="marketing", entities={"type": "social"})
        
        self.assertEqual(result["team"], "Team Marketing")
        self.assertEqual(result["intent"], "marketing")
        self.assertEqual(result["status"], "created")
        self.assertIn("task_id", result)
    
    def test_route_dev(self):
        """Test routing dev intent to Team Dev."""
        result = self.router.route(intent="dev", entities={"component": "api"})
        
        self.assertEqual(result["team"], "Team Dev")
        self.assertEqual(result["intent"], "dev")
        self.assertEqual(result["status"], "created")
    
    def test_route_research(self):
        """Test routing research intent to Team Research."""
        result = self.router.route(intent="research", entities={"topic": "ai"})
        
        self.assertEqual(result["team"], "Team Research")
        self.assertEqual(result["intent"], "research")
        self.assertEqual(result["status"], "created")
    
    def test_route_design(self):
        """Test routing design intent to Team Design."""
        result = self.router.route(intent="design", entities={"mockup": "homepage"})
        
        self.assertEqual(result["team"], "Team Design")
        self.assertEqual(result["intent"], "design")
        self.assertEqual(result["status"], "created")
    
    def test_route_office(self):
        """Test routing office intent to Team Office."""
        result = self.router.route(intent="office", entities={"task": "reports"})
        
        self.assertEqual(result["team"], "Team Office")
        self.assertEqual(result["intent"], "office")
        self.assertEqual(result["status"], "created")
    
    def test_route_unknown_intent(self):
        """Test routing unknown intent falls back to Team Unknown."""
        result = self.router.route(intent="unknown_intent", entities={})
        
        self.assertEqual(result["team"], "Team Unknown")
        self.assertEqual(result["status"], "created")
    
    def test_route_preserves_entities(self):
        """Test that entities are preserved in routing."""
        entities = {"key1": "value1", "key2": "value2"}
        result = self.router.route(intent="marketing", entities=entities)
        
        self.assertEqual(result["entities"], entities)
    
    def test_route_empty_intent_raises(self):
        """Test that empty intent raises ValueError."""
        with self.assertRaises(ValueError):
            self.router.route(intent="")
    
    def test_route_none_entities(self):
        """Test that None entities defaults to empty dict."""
        result = self.router.route(intent="dev", entities=None)
        
        self.assertEqual(result["entities"], {})
    
    def test_route_with_description(self):
        """Test routing with custom description."""
        result = self.router.route(
            intent="design",
            entities={},
            description="Create new logo"
        )
        
        self.assertIn("description", result)
        self.assertEqual(result["description"], "Create new logo")


class TestBatchRouting(unittest.TestCase):
    """Test batch routing functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.router = TaskRouter(use_mock_tasks=True)
    
    def test_batch_routing(self):
        """Test routing multiple tasks at once."""
        tasks = [
            {"intent": "marketing", "entities": {"campaign": "a"}},
            {"intent": "dev", "entities": {"feature": "b"}},
            {"intent": "research", "entities": {"topic": "c"}},
        ]
        
        results = self.router.route_batch(tasks)
        
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["team"], "Team Marketing")
        self.assertEqual(results[1]["team"], "Team Dev")
        self.assertEqual(results[2]["team"], "Team Research")
    
    def test_batch_routing_preserves_order(self):
        """Test that batch routing preserves task order."""
        tasks = [
            {"intent": "design"},
            {"intent": "office"},
        ]
        
        results = self.router.route_batch(tasks)
        
        self.assertEqual(results[0]["team"], "Team Design")
        self.assertEqual(results[1]["team"], "Team Office")


class TestConvenienceFunction(unittest.TestCase):
    """Test the convenience route_task function."""
    
    def test_route_task_creates_router(self):
        """Test that route_task creates router and routes correctly."""
        result = route_task(
            intent="marketing",
            entities={"type": "email"}
        )
        
        self.assertEqual(result["team"], "Team Marketing")
        self.assertEqual(result["status"], "created")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.router = TaskRouter(use_mock_tasks=True)
    
    def test_case_insensitive_intent(self):
        """Test that intents are case-insensitive."""
        result1 = self.router.route(intent="MARKETING")
        result2 = self.router.route(intent="Marketing")
        result3 = self.router.route(intent="mArKeTiNg")
        
        self.assertEqual(result1["team"], result2["team"])
        self.assertEqual(result2["team"], result3["team"])
    
    def test_whitespace_intent(self):
        """Test that whitespace is trimmed from intents."""
        result = self.router.route(intent="  dev  ")
        
        self.assertEqual(result["team"], "Team Dev")
    
    def test_intent_variations(self):
        """Test variations of dev intent."""
        result1 = self.router.route(intent="dev")
        result2 = self.router.route(intent="development")
        
        self.assertEqual(result1["team"], result2["team"])
    
    def test_empty_entities_dict(self):
        """Test routing with empty entities dict."""
        result = self.router.route(intent="office", entities={})
        
        self.assertEqual(result["entities"], {})
        self.assertEqual(result["status"], "created")
    
    def test_special_characters_in_intent(self):
        """Test intent with special characters falls to unknown."""
        result = self.router.route(intent="dev@123")
        
        self.assertEqual(result["team"], "Team Unknown")
    
    def test_numbers_as_intent(self):
        """Test that numeric intent falls to unknown."""
        result = self.router.route(intent="12345")
        
        self.assertEqual(result["team"], "Team Unknown")


if __name__ == "__main__":
    unittest.main(verbosity=2)
