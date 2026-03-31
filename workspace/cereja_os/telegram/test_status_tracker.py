"""
Tests for Status Tracker Module

Run with: python -m pytest test_status_tracker.py -v
Or directly: python test_status_tracker.py
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from status_tracker import (
    StatusTracker,
    SubscriptionStore,
    TaskCache,
    OpenMOSSClient,
    TaskStatus,
    Subscription,
    parse_status_command,
    parse_cancel_command,
    handle_command,
)


class TestParseCommands(unittest.TestCase):
    """Test command parsing"""

    def test_parse_status_command_valid(self):
        task_id = parse_status_command("/status abc123")
        self.assertEqual(task_id, "abc123")

    def test_parse_status_command_with_spaces(self):
        task_id = parse_status_command("/status   task-456  ")
        self.assertEqual(task_id, "task-456")

    def test_parse_status_command_invalid_no_args(self):
        task_id = parse_status_command("/status")
        self.assertIsNone(task_id)

    def test_parse_cancel_command_valid(self):
        task_id = parse_cancel_command("/cancel xyz789")
        self.assertEqual(task_id, "xyz789")

    def test_parse_cancel_command_invalid(self):
        task_id = parse_cancel_command("/cancel")
        self.assertIsNone(task_id)


class TestTaskStatus(unittest.TestCase):
    """Test TaskStatus data model"""

    def test_to_card_format(self):
        task = TaskStatus(
            task_id="test-001",
            status="pending",
            team="dev-team",
            tenant_id="tenant-1",
            created_at="2026-03-29T10:00:00",
            updated_at="2026-03-29T12:30:00"
        )
        card = task.to_card()
        
        self.assertIn("test-001", card)
        self.assertIn("pending", card)
        self.assertIn("dev-team", card)
        self.assertIn("2026-03-29T10:00:00", card)
        self.assertIn("2026-03-29T12:30:00", card)


class TestSubscriptionStore(unittest.TestCase):
    """Test SubscriptionStore"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = SubscriptionStore(
            filepath=os.path.join(self.temp_dir, "subscriptions.json")
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_subscribe_new(self):
        result = self.store.subscribe("chat1", "task1", "tenant1", "pending")
        self.assertTrue(result)
        
        subs = self.store.get_subscriptions("task1")
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0].chat_id, "chat1")
        self.assertEqual(subs[0].task_id, "task1")

    def test_subscribe_duplicate(self):
        self.store.subscribe("chat1", "task1", "tenant1", "pending")
        self.store.subscribe("chat1", "task1", "tenant1", "pending")
        
        subs = self.store.get_subscriptions("task1")
        self.assertEqual(len(subs), 1)  # No duplicate

    def test_subscribe_multiple_chats(self):
        self.store.subscribe("chat1", "task1", "tenant1", "pending")
        self.store.subscribe("chat2", "task1", "tenant1", "in_progress")
        
        subs = self.store.get_subscriptions("task1")
        self.assertEqual(len(subs), 2)

    def test_unsubscribe_existing(self):
        self.store.subscribe("chat1", "task1", "tenant1", "pending")
        result = self.store.unsubscribe("chat1", "task1")
        
        self.assertTrue(result)
        self.assertEqual(len(self.store.get_subscriptions("task1")), 0)

    def test_unsubscribe_nonexistent(self):
        result = self.store.unsubscribe("chat1", "nonexistent")
        self.assertFalse(result)

    def test_persistence(self):
        self.store.subscribe("chat1", "task1", "tenant1", "pending")
        
        # Create new store instance (simulates restart)
        store2 = SubscriptionStore(
            filepath=os.path.join(self.temp_dir, "subscriptions.json")
        )
        
        subs = store2.get_subscriptions("task1")
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0].chat_id, "chat1")


class TestTaskCache(unittest.TestCase):
    """Test TaskCache"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = TaskCache(
            filepath=os.path.join(self.temp_dir, "cache.json")
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_set_and_get(self):
        task = TaskStatus(
            task_id="task-001",
            status="completed",
            team="qa-team",
            tenant_id="tenant-2",
            created_at="2026-03-29T08:00:00",
            updated_at="2026-03-29T16:00:00"
        )
        
        self.cache.set(task)
        retrieved = self.cache.get("task-001")
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.task_id, "task-001")
        self.assertEqual(retrieved.status, "completed")

    def test_get_nonexistent(self):
        result = self.cache.get("nonexistent")
        self.assertIsNone(result)

    def test_delete(self):
        task = TaskStatus(
            task_id="task-del",
            status="pending",
            team="team",
            tenant_id="t",
            created_at="",
            updated_at=""
        )
        self.cache.set(task)
        self.assertTrue(self.cache.delete("task-del"))
        self.assertIsNone(self.cache.get("task-del"))

    def test_delete_nonexistent(self):
        self.assertFalse(self.cache.delete("nonexistent"))

    def test_persistence(self):
        task = TaskStatus(
            task_id="persist-task",
            status="in_progress",
            team="dev",
            tenant_id="t1",
            created_at="",
            updated_at=""
        )
        self.cache.set(task)
        
        cache2 = TaskCache(filepath=os.path.join(self.temp_dir, "cache.json"))
        retrieved = cache2.get("persist-task")
        
        self.assertEqual(retrieved.status, "in_progress")


class MockOpenMOSSClient:
    """Mock OpenMOSS client for testing"""

    def __init__(self):
        self.tasks = {
            "task-001": {
                "status": "pending",
                "team": "dev-team",
                "tenant_id": "tenant-1",
                "created_at": "2026-03-29T10:00:00",
                "updated_at": "2026-03-29T12:00:00"
            },
            "task-002": {
                "status": "completed",
                "team": "qa-team",
                "tenant_id": "tenant-1",
                "created_at": "2026-03-28T08:00:00",
                "updated_at": "2026-03-29T14:00:00"
            },
            "task-003": {
                "status": "in_progress",
                "team": "ops-team",
                "tenant_id": "tenant-2",
                "created_at": "2026-03-27T09:00:00",
                "updated_at": "2026-03-29T11:00:00"
            }
        }
        self.deleted = set()

    def get_task(self, task_id, tenant_id=None):
        task = self.tasks.get(task_id)
        if task:
            return {"task_id": task_id, **task}
        return None

    def delete_task(self, task_id, tenant_id=None):
        if task_id in self.tasks:
            del self.tasks[task_id]
            self.deleted.add(task_id)
            return True
        return False


class TestStatusTracker(unittest.TestCase):
    """Test StatusTracker service"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_client = MockOpenMOSSClient()
        self.tracker = StatusTracker(
            openmoss_client=self.mock_client,
            subscription_store=SubscriptionStore(
                filepath=os.path.join(self.temp_dir, "subs.json")
            ),
            task_cache=TaskCache(
                filepath=os.path.join(self.temp_dir, "cache.json")
            )
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_task_status_from_api(self):
        task = self.tracker.get_task_status("task-001")
        
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.team, "dev-team")

    def test_get_task_status_not_found(self):
        task = self.tracker.get_task_status("nonexistent")
        self.assertIsNone(task)

    def test_handle_status_command_success(self):
        response = self.tracker.handle_status_command("task-001")
        
        self.assertIn("task-001", response)
        self.assertIn("pending", response)
        self.assertIn("dev-team", response)

    def test_handle_status_command_not_found(self):
        response = self.tracker.handle_status_command("nonexistent")
        
        self.assertIn("não encontrada", response)

    def test_handle_cancel_pending_task(self):
        response = self.tracker.handle_cancel_command("task-001")
        
        self.assertIn("cancelada", response)
        self.assertIn("sucesso", response)

    def test_handle_cancel_completed_task_rejected(self):
        response = self.tracker.handle_cancel_command("task-002")
        
        self.assertIn("Não é possível cancelar", response)
        self.assertIn("completed", response)

    def test_handle_cancel_in_progress_task_rejected(self):
        response = self.tracker.handle_cancel_command("task-003")
        
        self.assertIn("Não é possível cancelar", response)
        self.assertIn("in_progress", response)

    def test_subscribe(self):
        response = self.tracker.subscribe("chat123", "task-001")
        
        self.assertIn("Subscrito", response)
        self.assertIn("pending", response)

    def test_unsubscribe(self):
        self.tracker.subscribe("chat123", "task-001")
        response = self.tracker.unsubscribe("chat123", "task-001")
        
        self.assertIn("Desinscrito", response)

    def test_check_and_notify_status_change(self):
        # Subscribe first
        self.tracker.subscribe("chat123", "task-001")
        
        # Simulate status change
        self.mock_client.tasks["task-001"]["status"] = "in_progress"
        
        notifications = self.tracker.check_and_notify("task-001")
        
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[0]["chat_id"], "chat123")
        self.assertEqual(notifications[0]["old_status"], "pending")
        self.assertEqual(notifications[0]["new_status"], "in_progress")


class TestHandleCommand(unittest.TestCase):
    """Test handle_command function"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_client = MockOpenMOSSClient()
        
        # Patch get_tracker to return our test tracker
        self.patcher = patch('status_tracker.get_tracker')
        self.mock_get_tracker = self.patcher.start()
        self.mock_get_tracker.return_value = StatusTracker(
            openmoss_client=self.mock_client,
            subscription_store=SubscriptionStore(
                filepath=os.path.join(self.temp_dir, "subs.json")
            ),
            task_cache=TaskCache(
                filepath=os.path.join(self.temp_dir, "cache.json")
            )
        )

    def tearDown(self):
        self.patcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_handle_status_command(self):
        response = handle_command("status", "/status task-001")
        self.assertIn("task-001", response)
        self.assertIn("pending", response)

    def test_handle_status_command_no_args(self):
        response = handle_command("status", "/status")
        self.assertIn("Uso", response)

    def test_handle_cancel_command(self):
        response = handle_command("cancel", "/cancel task-001")
        self.assertIn("cancelada", response)

    def test_handle_cancel_command_no_args(self):
        response = handle_command("cancel", "/cancel")
        self.assertIn("Uso", response)

    def test_handle_unknown_command(self):
        response = handle_command("unknown", "/unknown")
        self.assertIn("Comando desconhecido", response)


class TestPermissionValidation(unittest.TestCase):
    """Test permission and authorization logic"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mock_client = MockOpenMOSSClient()
        self.tracker = StatusTracker(
            openmoss_client=self.mock_client,
            subscription_store=SubscriptionStore(
                filepath=os.path.join(self.temp_dir, "subs.json")
            ),
            task_cache=TaskCache(
                filepath=os.path.join(self.temp_dir, "cache.json")
            )
        )

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cancel_only_allows_pending(self):
        """Verify only pending tasks can be cancelled"""
        # Pending - should succeed
        result = self.tracker.handle_cancel_command("task-001")
        self.assertIn("sucesso", result)
        
        # Completed - should be rejected
        result = self.tracker.handle_cancel_command("task-002")
        self.assertIn("Não é possível", result)
        
        # In Progress - should be rejected
        result = self.tracker.handle_cancel_command("task-003")
        self.assertIn("Não é possível", result)

    def test_tenant_isolation(self):
        """Verify tenant data isolation"""
        # Subscribe with tenant-1
        self.tracker.subscribe("chat1", "task-001", tenant_id="tenant-1")
        
        # Check notifications respect tenant boundaries
        subs = self.tracker.subscriptions.get_subscriptions("task-001")
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0].tenant_id, "tenant-1")


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    # Run with pytest if available, otherwise unittest
    try:
        import pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        unittest.main(verbosity=2)
