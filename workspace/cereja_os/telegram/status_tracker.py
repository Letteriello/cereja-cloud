"""
Status Tracker Module for Cereja OS Telegram Bot

Provides task status tracking, /status and /cancel commands,
and automatic notifications on status changes.
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

STORAGE_DIR = os.path.join(os.path.dirname(__file__), "data")
SUBSCRIPTIONS_FILE = os.path.join(STORAGE_DIR, "subscriptions.json")
TASKS_CACHE_FILE = os.path.join(STORAGE_DIR, "tasks_cache.json")

# ============================================================================
# Data Models
# ============================================================================

@dataclass
class TaskStatus:
    """Task status data model"""
    task_id: str
    status: str
    team: str
    tenant_id: str
    created_at: str
    updated_at: str

    def to_card(self) -> str:
        """Format task status as a Telegram card"""
        return (
            f"📋 Task: {self.task_id}\n"
            f"🏢 Time: {self.team}\n"
            f"📊 Status: {self.status}\n"
            f"⏰ Criado: {self.created_at}\n"
            f"🔄 Atualizado: {self.updated_at}"
        )


@dataclass
class Subscription:
    """Subscription for status change notifications"""
    chat_id: str
    task_id: str
    tenant_id: str
    last_status: str
    subscribed_at: str


# ============================================================================
# Storage Layer
# ============================================================================

class SubscriptionStore:
    """Manages subscriptions for status change notifications"""

    def __init__(self, filepath: str = SUBSCRIPTIONS_FILE):
        self.filepath = filepath
        self._ensure_storage_dir()
        self._subscriptions: Dict[str, List[Subscription]] = {}  # task_id -> [subscriptions]
        self._load()

    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def _load(self):
        """Load subscriptions from disk"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    self._subscriptions = {
                        task_id: [Subscription(**sub) for sub in subs]
                        for task_id, subs in data.items()
                    }
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to load subscriptions: {e}")
                self._subscriptions = {}

    def _save(self):
        """Save subscriptions to disk"""
        try:
            data = {
                task_id: [asdict(sub) for sub in subs]
                for task_id, subs in self._subscriptions.items()
            }
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save subscriptions: {e}")

    def subscribe(self, chat_id: str, task_id: str, tenant_id: str, current_status: str) -> bool:
        """Subscribe a chat to task status updates"""
        if task_id not in self._subscriptions:
            self._subscriptions[task_id] = []

        # Check if already subscribed
        for sub in self._subscriptions[task_id]:
            if sub.chat_id == chat_id:
                sub.last_status = current_status
                self._save()
                return True

        subscription = Subscription(
            chat_id=chat_id,
            task_id=task_id,
            tenant_id=tenant_id,
            last_status=current_status,
            subscribed_at=datetime.now(timezone.utc).isoformat()
        )
        self._subscriptions[task_id].append(subscription)
        self._save()
        return True

    def unsubscribe(self, chat_id: str, task_id: str) -> bool:
        """Unsubscribe a chat from task updates"""
        if task_id in self._subscriptions:
            before = len(self._subscriptions[task_id])
            self._subscriptions[task_id] = [
                sub for sub in self._subscriptions[task_id]
                if sub.chat_id != chat_id
            ]
            after = len(self._subscriptions[task_id])
            if before != after:
                self._save()
                return True
        return False

    def get_subscriptions(self, task_id: str) -> List[Subscription]:
        """Get all subscriptions for a task"""
        return self._subscriptions.get(task_id, [])

    def get_chat_subscriptions(self, chat_id: str) -> List[Subscription]:
        """Get all subscriptions for a chat"""
        result = []
        for subs in self._subscriptions.values():
            result.extend(sub for sub in subs if sub.chat_id == chat_id)
        return result


class TaskCache:
    """Simple file-based cache for task data"""

    def __init__(self, filepath: str = TASKS_CACHE_FILE):
        self.filepath = filepath
        self._ensure_storage_dir()
        self._cache: Dict[str, TaskStatus] = {}
        self._load()

    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def _load(self):
        """Load cache from disk"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    self._cache = {k: TaskStatus(**v) for k, v in data.items()}
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to load task cache: {e}")
                self._cache = {}

    def _save(self):
        """Save cache to disk"""
        try:
            data = {k: asdict(v) for k, v in self._cache.items()}
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save task cache: {e}")

    def get(self, task_id: str) -> Optional[TaskStatus]:
        """Get cached task status"""
        return self._cache.get(task_id)

    def set(self, task: TaskStatus):
        """Cache task status"""
        self._cache[task.task_id] = task
        self._save()

    def delete(self, task_id: str) -> bool:
        """Remove task from cache"""
        if task_id in self._cache:
            del self._cache[task_id]
            self._save()
            return True
        return False


# ============================================================================
# API Client (OpenMOSS Integration)
# ============================================================================

class OpenMOSSClient:
    """Client for OpenMOSS API"""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.environ.get("OPENMOSS_API_URL", "http://localhost:3000")
        self.api_key = api_key or os.environ.get("OPENMOSS_API_KEY", "")

    def _headers(self) -> Dict[str, str]:
        """Build request headers"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def get_task(self, task_id: str, tenant_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Fetch task from OpenMOSS API
        
        Args:
            task_id: The task ID to fetch
            tenant_id: Optional tenant ID for multi-tenant access
            
        Returns:
            Task data dict or None if not found
        """
        try:
            import urllib.request
            
            url = f"{self.base_url}/api/tasks/{task_id}"
            if tenant_id:
                url += f"?tenant_id={tenant_id}"
            
            req = urllib.request.Request(
                url,
                headers=self._headers()
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data.get("task") or data
            
        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP {e.code} fetching task {task_id}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            logger.warning(f"Network error fetching task {task_id}: {e.reason}")
            return None
        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}")
            return None

    def delete_task(self, task_id: str, tenant_id: str = None) -> bool:
        """
        Delete a task via OpenMOSS API
        
        Args:
            task_id: The task ID to delete
            tenant_id: Optional tenant ID
            
        Returns:
            True if deleted successfully
        """
        try:
            import urllib.request
            import urllib.error
            
            url = f"{self.base_url}/api/tasks/{task_id}"
            if tenant_id:
                url += f"?tenant_id={tenant_id}"
            
            req = urllib.request.Request(
                url,
                headers=self._headers(),
                method="DELETE"
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
            
        except urllib.error.HTTPError as e:
            logger.warning(f"HTTP {e.code} deleting task {task_id}: {e.reason}")
            return False
        except urllib.error.URLError as e:
            logger.warning(f"Network error deleting task {task_id}: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            return False


# ============================================================================
# Status Tracker Service
# ============================================================================

class StatusTracker:
    """
    Main status tracking service
    
    Provides:
    - Task status queries via get_task_status()
    - /status command handling
    - /cancel command handling
    - Automatic status change notifications
    """

    def __init__(
        self,
        openmoss_client: OpenMOSSClient = None,
        subscription_store: SubscriptionStore = None,
        task_cache: TaskCache = None
    ):
        self.client = openmoss_client or OpenMOSSClient()
        self.subscriptions = subscription_store or SubscriptionStore()
        self.cache = task_cache or TaskCache()

    def get_task_status(self, task_id: str, tenant_id: str = None) -> Optional[TaskStatus]:
        """
        Get task status - checks cache first, then API
        
        Args:
            task_id: The task ID to look up
            tenant_id: Optional tenant ID
            
        Returns:
            TaskStatus object or None if not found
        """
        # Check cache first
        cached = self.cache.get(task_id)
        
        # Try to fetch fresh from API
        task_data = self.client.get_task(task_id, tenant_id)
        
        if task_data:
            task = TaskStatus(
                task_id=task_id,
                status=task_data.get("status", "unknown"),
                team=task_data.get("team", "N/A"),
                tenant_id=tenant_id or task_data.get("tenant_id", ""),
                created_at=task_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                updated_at=task_data.get("updated_at", datetime.now(timezone.utc).isoformat())
            )
            self.cache.set(task)
            return task
        
        # Fall back to cache if API fails
        if cached:
            return cached
        
        return None

    def handle_status_command(self, task_id: str, tenant_id: str = None) -> str:
        """
        Handle /status <task_id> command
        
        Args:
            task_id: The task ID to query
            tenant_id: Optional tenant ID
            
        Returns:
            Formatted status card string
        """
        task = self.get_task_status(task_id, tenant_id)
        
        if not task:
            return f"❌ Task `{task_id}` não encontrada."
        
        return task.to_card()

    def handle_cancel_command(
        self,
        task_id: str,
        tenant_id: str = None,
        force_tenant_check: bool = False
    ) -> str:
        """
        Handle /cancel <task_id> command
        
        Only allows cancellation if task status is 'pending'
        
        Args:
            task_id: The task ID to cancel
            tenant_id: Optional tenant ID
            force_tenant_check: If True, verify tenant ownership
            
        Returns:
            Cancellation result message
        """
        task = self.get_task_status(task_id, tenant_id)
        
        if not task:
            return f"❌ Task `{task_id}` não encontrada."
        
        # Only allow cancellation of pending tasks
        if task.status.lower() != "pending":
            return (
                f"⚠️ Não é possível cancelar task `{task_id}`\n"
                f"Status atual: **{task.status}**\n"
                f"Só tasks com status *pending* podem ser canceladas."
            )
        
        # Attempt deletion via API
        success = self.client.delete_task(task_id, tenant_id)
        
        if success:
            # Update cache
            self.cache.delete(task_id)
            
            # Notify subscribers
            self._notify_status_change(task_id, "cancelled", tenant_id)
            
            return f"✅ Task `{task_id}` cancelada com sucesso!"
        
        return (
            f"❌ Falha ao cancelar task `{task_id}`\n"
            f"Tente novamente ou contacte o suporte."
        )

    def subscribe(self, chat_id: str, task_id: str, tenant_id: str = None) -> str:
        """
        Subscribe to status updates for a task
        
        Args:
            chat_id: Telegram chat ID
            task_id: Task ID to subscribe to
            tenant_id: Optional tenant ID
            
        Returns:
            Subscription confirmation message
        """
        task = self.get_task_status(task_id, tenant_id)
        
        if not task:
            return f"❌ Task `{task_id}` não encontrada."
        
        self.subscriptions.subscribe(chat_id, task_id, tenant_id or task.tenant_id, task.status)
        
        return (
            f"🔔 Subscrito!\n"
            f"Você será notificado quando a task `{task_id}` for atualizada.\n"
            f"Status atual: **{task.status}**"
        )

    def unsubscribe(self, chat_id: str, task_id: str) -> str:
        """Unsubscribe from task updates"""
        if self.subscriptions.unsubscribe(chat_id, task_id):
            return f"🔕 Desinscrito da task `{task_id}`."
        return f"ℹ️ Não há subscription para task `{task_id}` neste chat."

    def _notify_status_change(
        self,
        task_id: str,
        new_status: str,
        tenant_id: str = None
    ) -> List[Dict[str, str]]:
        """
        Notify subscribers of status change
        
        Returns:
            List of notification results (chat_id -> status)
        """
        notifications = []
        subs = self.subscriptions.get_subscriptions(task_id)
        
        for sub in subs:
            # Verify tenant access
            if tenant_id and sub.tenant_id != tenant_id:
                continue
            
            notifications.append({
                "chat_id": sub.chat_id,
                "task_id": task_id,
                "status": new_status,
                "message": (
                    f"🔔 *Update*: Task `{task_id}`\n"
                    f"📊 Novo status: **{new_status}**"
                )
            })
        
        return notifications

    def check_and_notify(
        self,
        task_id: str,
        tenant_id: str = None
    ) -> List[Dict[str, str]]:
        """
        Check task status and notify if changed
        
        Args:
            task_id: Task ID to check
            tenant_id: Optional tenant ID
            
        Returns:
            List of notifications to send
        """
        task = self.get_task_status(task_id, tenant_id)
        
        if not task:
            return []
        
        subs = self.subscriptions.get_subscriptions(task_id)
        notifications = []
        
        for sub in subs:
            # Verify tenant access
            if tenant_id and sub.tenant_id != tenant_id:
                continue
            
            # Check if status changed
            if sub.last_status != task.status:
                notifications.append({
                    "chat_id": sub.chat_id,
                    "task_id": task_id,
                    "old_status": sub.last_status,
                    "new_status": task.status,
                    "message": (
                        f"🔔 *Update*: Task `{task_id}`\n"
                        f"📊 De: *{sub.last_status}*\n"
                        f"📊 Para: **{task.status}**"
                    )
                })
                # Update subscription
                self.subscriptions.subscribe(
                    sub.chat_id, task_id, sub.tenant_id, task.status
                )
        
        return notifications


# ============================================================================
# Telegram Command Handlers
# ============================================================================

def parse_status_command(text: str) -> Optional[str]:
    """
    Parse /status command text
    
    Args:
        text: Full command text (e.g., "/status abc123")
        
    Returns:
        Task ID or None if invalid
    """
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return None
    return parts[1].strip()


def parse_cancel_command(text: str) -> Optional[str]:
    """
    Parse /cancel command text
    
    Args:
        text: Full command text (e.g., "/cancel abc123")
        
    Returns:
        Task ID or None if invalid
    """
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return None
    return parts[1].strip()


# ============================================================================
# Module Entry Point
# ============================================================================

# Singleton instance
_tracker: Optional[StatusTracker] = None


def get_tracker() -> StatusTracker:
    """Get or create the global StatusTracker instance"""
    global _tracker
    if _tracker is None:
        _tracker = StatusTracker()
    return _tracker


def handle_command(command: str, text: str, chat_id: str = None, tenant_id: str = None) -> str:
    """
    Handle a Telegram command
    
    Args:
        command: Command name (e.g., "status", "cancel")
        text: Full message text
        chat_id: Telegram chat ID
        tenant_id: Optional tenant ID
        
    Returns:
        Response message
    """
    tracker = get_tracker()
    
    if command == "status":
        task_id = parse_status_command(text)
        if not task_id:
            return "📋 Uso: /status <task_id>"
        return tracker.handle_status_command(task_id, tenant_id)
    
    elif command == "cancel":
        task_id = parse_cancel_command(text)
        if not task_id:
            return "❌ Uso: /cancel <task_id>"
        return tracker.handle_cancel_command(task_id, tenant_id)
    
    elif command == "subscribe":
        task_id = parse_status_command(text)
        if not task_id:
            return "🔔 Uso: /subscribe <task_id>"
        if not chat_id:
            return "❌ Erro interno: chat_id não disponível"
        return tracker.subscribe(chat_id, task_id, tenant_id)
    
    elif command == "unsubscribe":
        task_id = parse_cancel_command(text)
        if not task_id:
            return "🔕 Uso: /unsubscribe <task_id>"
        if not chat_id:
            return "❌ Erro interno: chat_id não disponível"
        return tracker.unsubscribe(chat_id, task_id)
    
    return f"❓ Comando desconhecido: /{command}"
