"""
test_handlers.py - Unit tests for Telegram Order Flow Handlers

Tests validation logic, confirmation message format, and error handling.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

# Import the module under test
import sys
sys.path.insert(0, '/root/OpenMOSS/workspace/cereja_os')

from telegram.handlers import (
    validate_message,
    get_validation_error_message,
    format_confirmation_message,
    format_error_message,
    handle_order_text,
    MIN_MESSAGE_LENGTH,
    MAX_MESSAGE_LENGTH,
    OrderValidationError,
    OrchestratorError,
    IntentUncertainError,
)


class TestValidateMessage:
    """Test suite for message validation logic."""

    def test_valid_message_length_min(self):
        """Test minimum valid message length (10 characters)."""
        message = "a" * 10
        assert validate_message(message) is True

    def test_valid_message_length_max(self):
        """Test maximum valid message length (2000 characters)."""
        message = "a" * 2000
        assert validate_message(message) is True

    def test_valid_message_typical(self):
        """Test typical valid message."""
        message = "Preciso de um site para meu restaurante"
        assert validate_message(message) is True

    def test_invalid_message_too_short(self):
        """Test message shorter than minimum."""
        message = "a" * 9
        assert validate_message(message) is False

    def test_invalid_message_too_long(self):
        """Test message longer than maximum."""
        message = "a" * 2001
        assert validate_message(message) is False

    def test_invalid_message_empty(self):
        """Test empty message."""
        assert validate_message("") is False
        assert validate_message(None) is False

    def test_invalid_message_whitespace_only(self):
        """Test whitespace-only message."""
        assert validate_message("   ") is False
        assert validate_message("\t\n") is False

    def test_invalid_message_non_string(self):
        """Test non-string input."""
        assert validate_message(123) is False
        assert validate_message([]) is False
        assert validate_message({}) is False

    def test_message_with_leading_trailing_whitespace(self):
        """Test message with leading/trailing whitespace is trimmed."""
        message = "  " + "a" * 15 + "  "
        # This should fail because trimmed length is valid but validation checks raw
        # Actually, let's check the actual behavior
        result = validate_message(message)
        # The message has 19 chars total, so it should be valid
        assert result is True


class TestGetValidationErrorMessage:
    """Test suite for validation error message generation."""

    def test_none_message_returns_error(self):
        """Test None message returns appropriate error."""
        msg = get_validation_error_message(None)
        assert msg is not None
        assert "10 caracteres" in msg
        assert "❌" in msg

    def test_empty_message_returns_error(self):
        """Test empty message returns appropriate error."""
        msg = get_validation_error_message("")
        assert msg is not None
        assert "10 caracteres" in msg

    def test_short_message_returns_error(self):
        """Test short message returns appropriate error."""
        msg = get_validation_error_message("abc")
        assert msg is not None
        assert "10 caracteres" in msg

    def test_valid_message_returns_none(self):
        """Test valid message returns None."""
        msg = get_validation_error_message("a" * 10)
        assert msg is None

    def test_long_message_returns_error(self):
        """Test long message returns appropriate error."""
        msg = get_validation_error_message("a" * 2001)
        assert msg is not None
        assert "2000" in msg


class TestFormatConfirmationMessage:
    """Test suite for confirmation message formatting."""

    def test_confirmation_format_basic(self):
        """Test basic confirmation message format."""
        msg = format_confirmation_message("ABC12345", "dev", "pending")
        
        assert "✅ Pedido recebido!" in msg
        assert "ABC12345" in msg
        assert "dev" in msg
        assert "Aguardando execução" in msg
        assert "/status ABC12345" in msg

    def test_confirmation_format_different_status(self):
        """Test confirmation with different statuses."""
        msg = format_confirmation_message("XYZ99999", "design", "in_progress")
        
        assert "Em execução" in msg
        assert "design" in msg

    def test_confirmation_format_completed(self):
        """Test confirmation with completed status."""
        msg = format_confirmation_message("TASK001", "qa", "completed")
        
        assert "Concluído" in msg

    def test_confirmation_contains_all_required_elements(self):
        """Test that confirmation contains all required elements."""
        msg = format_confirmation_message("TEST123", "team", "pending")
        
        required_elements = [
            "✅",
            "📋",
            "🏢",
            "📊",
            "Task ID:",
            "Time:",
            "Status:",
            "/status"
        ]
        
        for element in required_elements:
            assert element in msg, f"Missing element: {element}"


class TestFormatErrorMessage:
    """Test suite for error message formatting."""

    def test_validation_error_message(self):
        """Test validation error message format."""
        msg = format_error_message("validation")
        
        assert "❌" in msg
        assert "10 caracteres" in msg

    def test_orchestrator_error_message(self):
        """Test orchestrator error message format."""
        msg = format_error_message("orchestrator")
        
        assert "❌" in msg
        assert "Ops, algo deu errado" in msg

    def test_uncertain_intent_error_message(self):
        """Test uncertain intent error message format."""
        msg = format_error_message("uncertain")
        
        assert "🤔" in msg
        assert "reformular" in msg

    def test_unknown_error_type_defaults_to_orchestrator(self):
        """Test unknown error type defaults to orchestrator message."""
        msg = format_error_message("unknown_type")
        
        assert "❌" in msg
        assert "Ops, algo deu errado" in msg


class TestHandleOrderText:
    """Test suite for main order text handler."""

    @pytest.mark.asyncio
    async def test_valid_order_returns_confirmation(self):
        """Test that valid order returns success confirmation."""
        with patch('telegram.handlers.ORCHESTRATOR_AVAILABLE', True):
            with patch('telegram.handlers.process_through_orchestrator') as mock_process:
                mock_process.return_value = ("TASK123", "dev", "pending")
                
                msg, success = await handle_order_text(
                    "Preciso de um site para meu restaurante",
                    chat_id=123456789,
                    tenant_id="tenant_001"
                )
                
                assert success is True
                assert "✅ Pedido recebido!" in msg
                assert "TASK123" in msg
                mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_short_order_returns_error(self):
        """Test that short order returns validation error."""
        msg, success = await handle_order_text(
            "abc",
            chat_id=123456789,
            tenant_id="tenant_001"
        )
        
        assert success is False
        assert "❌" in msg
        assert "10 caracteres" in msg

    @pytest.mark.asyncio
    async def test_empty_order_returns_error(self):
        """Test that empty order returns validation error."""
        msg, success = await handle_order_text(
            "",
            chat_id=123456789,
            tenant_id="tenant_001"
        )
        
        assert success is False
        assert "❌" in msg

    @pytest.mark.asyncio
    async def test_orchestrator_failure_returns_error(self):
        """Test that orchestrator failure returns appropriate error."""
        with patch('telegram.handlers.ORCHESTRATOR_AVAILABLE', True):
            with patch('telegram.handlers.process_through_orchestrator') as mock_process:
                mock_process.side_effect = OrchestratorError("Connection failed")
                
                msg, success = await handle_order_text(
                    "Preciso de um site para meu restaurante",
                    chat_id=123456789,
                    tenant_id="tenant_001"
                )
                
                assert success is False
                assert "❌" in msg
                assert "Ops, algo deu errado" in msg

    @pytest.mark.asyncio
    async def test_uncertain_intent_returns_error(self):
        """Test that uncertain intent returns appropriate error."""
        with patch('telegram.handlers.ORCHESTRATOR_AVAILABLE', True):
            with patch('telegram.handlers.process_through_orchestrator') as mock_process:
                mock_process.side_effect = IntentUncertainError("Low confidence")
                
                msg, success = await handle_order_text(
                    "Preciso de um site para meu restaurante",
                    chat_id=123456789,
                    tenant_id="tenant_001"
                )
                
                assert success is False
                assert "🤔" in msg
                assert "reformular" in msg

    @pytest.mark.asyncio
    async def test_long_order_returns_error(self):
        """Test that overly long order returns validation error."""
        long_message = "a" * 2001
        msg, success = await handle_order_text(
            long_message,
            chat_id=123456789,
            tenant_id="tenant_001"
        )
        
        assert success is False
        assert "❌" in msg
        assert "2000" in msg

    @pytest.mark.asyncio
    async def test_stub_orchestrator_when_not_available(self):
        """Test that stub orchestrator is used when modules unavailable."""
        with patch('telegram.handlers.ORCHESTRATOR_AVAILABLE', False):
            msg, success = await handle_order_text(
                "Preciso de um site para meu restaurante",
                chat_id=123456789,
                tenant_id="tenant_001"
            )
            
            assert success is True
            assert "✅ Pedido recebido!" in msg
            assert "Task ID:" in msg
            assert "default" in msg


class TestConstants:
    """Test suite for module constants."""

    def test_min_message_length(self):
        """Test minimum message length constant."""
        assert MIN_MESSAGE_LENGTH == 10

    def test_max_message_length(self):
        """Test maximum message length constant."""
        assert MAX_MESSAGE_LENGTH == 2000

    def test_min_less_than_max(self):
        """Test that min is less than max."""
        assert MIN_MESSAGE_LENGTH < MAX_MESSAGE_LENGTH


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
