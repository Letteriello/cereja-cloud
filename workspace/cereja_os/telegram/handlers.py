"""
handlers.py - Telegram Order Flow Handler for Cereja OS

This module handles incoming order messages from Telegram users,
validates them, and processes them through the Orchestrator pipeline.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Constants for validation
MIN_MESSAGE_LENGTH = 10
MAX_MESSAGE_LENGTH = 2000

# Try to import orchestrator components (ST 2.1, 2.2)
# These modules should exist after ST 2.1 and ST 2.2 are implemented
try:
    from orchestrator.intent_classifier import classify_intent
    from orchestrator.router import route_task
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    logger.warning("Orchestrator modules not available. Using stub implementations.")
    ORCHESTRATOR_AVAILABLE = False
    classify_intent = None
    route_task = None


class OrderValidationError(Exception):
    """Raised when order validation fails."""
    pass


class OrchestratorError(Exception):
    """Raised when orchestrator processing fails."""
    pass


class IntentUncertainError(Exception):
    """Raised when intent classification is uncertain."""
    pass


def validate_message(message_text: str) -> bool:
    """
    Validate the incoming message text.
    
    Args:
        message_text: The text message to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    if not message_text:
        return False
    if not isinstance(message_text, str):
        return False
    text = message_text.strip()
    if len(text) < MIN_MESSAGE_LENGTH or len(text) > MAX_MESSAGE_LENGTH:
        return False
    return True


def get_validation_error_message(message_text: str) -> Optional[str]:
    """
    Get appropriate error message for validation failure.
    
    Args:
        message_text: The text message that failed validation.
        
    Returns:
        Error message string or None if valid.
    """
    if not message_text:
        return "❌ Por favor, descreva seu pedido com mais detalhes (mínimo 10 caracteres)."
    
    text = message_text.strip()
    if len(text) < MIN_MESSAGE_LENGTH:
        return "❌ Por favor, descreva seu pedido com mais detalhes (mínimo 10 caracteres)."
    if len(text) > MAX_MESSAGE_LENGTH:
        return "❌ Seu pedido está muito longo (máximo 2000 caracteres). Tente dividi-lo em partes."
    
    return None


async def process_through_orchestrator(
    message_text: str,
    chat_id: int,
    tenant_id: str
) -> Tuple[str, str, str]:
    """
    Process the order through the Orchestrator (intent_classifier + router).
    
    Args:
        message_text: The validated order text.
        chat_id: Telegram chat ID.
        tenant_id: Tenant identifier.
        
    Returns:
        Tuple of (task_id, team, status)
        
    Raises:
        OrchestratorError: If orchestrator processing fails.
        IntentUncertainError: If intent cannot be determined.
    """
    if not ORCHESTRATOR_AVAILABLE:
        # Stub implementation for when orchestrator is not yet available
        # This allows testing and development to proceed
        import uuid
        task_id = str(uuid.uuid4())[:8].upper()
        return task_id, "default", "pending"
    
    try:
        # Step 1: Classify intent (ST 2.1)
        intent_result = classify_intent(message_text, tenant_id)
        
        if intent_result.get("confidence", 0) < 0.6:
            raise IntentUncertainError(
                "Intent classification confidence too low"
            )
        
        intent = intent_result.get("intent", "unknown")
        
        # Step 2: Route to appropriate team (ST 2.2)
        route_result = route_task(
            intent=intent,
            message=message_text,
            chat_id=chat_id,
            tenant_id=tenant_id
        )
        
        task_id = route_result.get("task_id", "unknown")
        team = route_result.get("team", "default")
        status = route_result.get("status", "pending")
        
        return task_id, team, status
        
    except IntentUncertainError:
        raise
    except Exception as e:
        logger.error(f"Orchestrator error: {e}")
        raise OrchestratorError(f"Failed to process through orchestrator: {e}")


def format_confirmation_message(task_id: str, team: str, status: str) -> str:
    """
    Format the confirmation message to send to the user.
    
    Args:
        task_id: The generated task ID.
        team: The assigned team.
        status: The initial task status.
        
    Returns:
        Formatted confirmation message.
    """
    status_display = {
        "pending": "Aguardando execução",
        "in_progress": "Em execução",
        "completed": "Concluído"
    }
    
    status_text = status_display.get(status, status)
    
    return f"""✅ Pedido recebido!
📋 Task ID: {task_id}
🏢 Time: {team}
📊 Status: {status_text}

Use /status {task_id} para acompanhar."""


def format_error_message(error_type: str) -> str:
    """
    Format an error message based on error type.
    
    Args:
        error_type: Type of error ('validation', 'orchestrator', 'uncertain')
        
    Returns:
        Formatted error message.
    """
    error_messages = {
        "validation": "❌ Por favor, descreva seu pedido com mais detalhes (mínimo 10 caracteres).",
        "orchestrator": "❌ Ops, algo deu errado. Tente novamente em alguns minutos.",
        "uncertain": "🤔 Não entendi. Pode reformular seu pedido?"
    }
    return error_messages.get(error_type, error_messages["orchestrator"])


async def handle_order_text(
    message_text: str,
    chat_id: int,
    tenant_id: str
) -> Tuple[str, bool]:
    """
    Main handler for incoming order text messages.
    
    This function:
    1. Validates the message (non-empty, 10-2000 chars)
    2. Processes through Orchestrator (intent_classifier + router)
    3. Returns confirmation message to the customer
    
    Args:
        message_text: The text message from the customer.
        chat_id: Telegram chat ID.
        tenant_id: Tenant identifier for multi-tenant support.
        
    Returns:
        Tuple of (response_message, success_flag)
        
    Example:
        >>> message, success = await handle_order_text(
        ...     "Preciso de um site para meu restaurante",
        ...     chat_id=123456789,
        ...     tenant_id="tenant_001"
        ... )
    """
    # Step 1: Validation
    error_msg = get_validation_error_message(message_text)
    if error_msg:
        logger.info(f"Validation failed for chat_id={chat_id}: {error_msg}")
        return error_msg, False
    
    # Step 2: Process through orchestrator
    try:
        task_id, team, status = await process_through_orchestrator(
            message_text=message_text.strip(),
            chat_id=chat_id,
            tenant_id=tenant_id
        )
        
        # Step 3: Format and return confirmation
        confirmation = format_confirmation_message(task_id, team, status)
        logger.info(f"Order processed successfully: task_id={task_id}, team={team}, chat_id={chat_id}")
        return confirmation, True
        
    except IntentUncertainError:
        error_msg = format_error_message("uncertain")
        logger.info(f"Intent uncertain for chat_id={chat_id}")
        return error_msg, False
        
    except OrchestratorError as e:
        error_msg = format_error_message("orchestrator")
        logger.error(f"Orchestrator error for chat_id={chat_id}: {e}")
        return error_msg, False
        
    except Exception as e:
        error_msg = format_error_message("orchestrator")
        logger.exception(f"Unexpected error processing order for chat_id={chat_id}: {e}")
        return error_msg, False
