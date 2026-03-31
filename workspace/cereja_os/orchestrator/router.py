"""
Task Routing Engine - ST 2.2
Cereja OS Orchestrator

Routes tasks to appropriate teams based on intent classification results.
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Team(Enum):
    """Available teams for task routing."""
    MARKETING = "Team Marketing"
    DEV = "Team Dev"
    RESEARCH = "Team Research"
    DESIGN = "Team Design"
    OFFICE = "Team Office"
    UNKNOWN = "Team Unknown"


class IntentMapping:
    """Maps intents to teams."""
    
    INTENT_TO_TEAM: Dict[str, Team] = {
        "marketing": Team.MARKETING,
        "dev": Team.DEV,
        "development": Team.DEV,
        "research": Team.RESEARCH,
        "design": Team.DESIGN,
        "office": Team.OFFICE,
    }
    
    @classmethod
    def get_team(cls, intent: str) -> Team:
        """Get team for a given intent."""
        normalized_intent = intent.lower().strip()
        return cls.INTENT_TO_TEAM.get(normalized_intent, Team.UNKNOWN)


class TaskCreator:
    """Handles task creation via OpenMOSS API or local mock."""
    
    def __init__(self, use_mock: bool = True, api_url: Optional[str] = None):
        """
        Initialize TaskCreator.
        
        Args:
            use_mock: If True, use mock task creation. If False, call real API.
            api_url: OpenMOSS API URL (required if use_mock=False).
        """
        self.use_mock = use_mock
        self.api_url = api_url or "http://localhost:8000"
    
    def create_task(
        self,
        intent: str,
        entities: Dict[str, Any],
        team: Team,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a subtask via OpenMOSS API or mock.
        
        Args:
            intent: The intent classification result.
            entities: Extracted entities from the input.
            team: Target team for the task.
            description: Optional task description.
            
        Returns:
            Dict containing task_id, team, intent, status, and metadata.
        """
        task_id = str(uuid.uuid4())
        
        task_data = {
            "task_id": task_id,
            "team": team.value,
            "intent": intent,
            "entities": entities,
            "status": "created",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": description or f"Task for {intent} routed to {team.value}",
        }
        
        if self.use_mock:
            logger.info(f"[MOCK] Task created: {task_data}")
        else:
            # Real API call would go here
            # response = requests.post(f"{self.api_url}/tasks", json=task_data)
            logger.info(f"[API] Task created via OpenMOSS: {task_id}")
        
        return task_data


class TeamNotifier:
    """Handles notification to team leaders."""
    
    def __init__(self, notification_mode: str = "log"):
        """
        Initialize TeamNotifier.
        
        Args:
            notification_mode: "log" (default), "message", or "webhook".
        """
        self.notification_mode = notification_mode
    
    def notify(
        self,
        task_id: str,
        team: Team,
        intent: str,
        entities: Dict[str, Any]
    ) -> bool:
        """
        Notify team leader about a new task.
        
        Args:
            task_id: The created task ID.
            team: Target team.
            intent: Intent that triggered the routing.
            entities: Extracted entities.
            
        Returns:
            True if notification sent successfully.
        """
        message = (
            f"[NOTIFICATION] New task assigned to {team.value}:\n"
            f"  Task ID: {task_id}\n"
            f"  Intent: {intent}\n"
            f"  Entities: {entities}"
        )
        
        if self.notification_mode == "log":
            logger.info(message)
            return True
        elif self.notification_mode == "message":
            # Placeholder for message sending (email, Slack, etc.)
            logger.info(f"[MESSAGE] Would send: {message}")
            return True
        elif self.notification_mode == "webhook":
            # Placeholder for webhook call
            logger.info(f"[WEBHOOK] Would call: {message}")
            return True
        
        return False


class TaskRouter:
    """
    Main router class that coordinates intent-to-team routing.
    
    Usage:
        router = TaskRouter()
        result = router.route(intent="marketing", entities={"campaign": "summer_sale"})
    """
    
    def __init__(
        self,
        use_mock_tasks: bool = True,
        notification_mode: str = "log",
        api_url: Optional[str] = None
    ):
        """
        Initialize TaskRouter.
        
        Args:
            use_mock_tasks: Use mock task creation (default True).
            notification_mode: How to notify teams ("log", "message", "webhook").
            api_url: OpenMOSS API URL for real task creation.
        """
        self.task_creator = TaskCreator(use_mock=use_mock_tasks, api_url=api_url)
        self.notifier = TeamNotifier(notification_mode=notification_mode)
    
    def route(
        self,
        intent: str,
        entities: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route a task to the appropriate team based on intent.
        
        Args:
            intent: The intent classification result (e.g., "marketing", "dev").
            entities: Optional dict of extracted entities.
            description: Optional task description.
            
        Returns:
            Dict with task_id, team, intent, status: "created", and metadata.
            
        Raises:
            ValueError: If intent is empty or invalid.
        """
        if not intent:
            raise ValueError("Intent cannot be empty")
        
        if entities is None:
            entities = {}
        
        # Map intent to team
        team = IntentMapping.get_team(intent)
        
        if team == Team.UNKNOWN:
            logger.warning(f"Unknown intent '{intent}', routing to fallback")
        
        # Create task
        task_result = self.task_creator.create_task(
            intent=intent,
            entities=entities,
            team=team,
            description=description
        )
        
        # Notify team leader
        self.notifier.notify(
            task_id=task_result["task_id"],
            team=team,
            intent=intent,
            entities=entities
        )
        
        return task_result
    
    def route_batch(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Route multiple tasks at once.
        
        Args:
            tasks: List of dicts, each with "intent" and optional "entities".
            
        Returns:
            List of routing results.
        """
        results = []
        for task in tasks:
            result = self.route(
                intent=task.get("intent", ""),
                entities=task.get("entities", {}),
                description=task.get("description")
            )
            results.append(result)
        
        return results


# Convenience function for simple usage
def route_task(
    intent: str,
    entities: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to route a single task.
    
    Args:
        intent: The intent classification result.
        entities: Optional dict of extracted entities.
        **kwargs: Additional arguments passed to TaskRouter.
        
    Returns:
        Dict with task_id, team, intent, status: "created".
    """
    router = TaskRouter(**kwargs)
    return router.route(intent=intent, entities=entities)
