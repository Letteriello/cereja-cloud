"""
Telegram Bot Configuration
Cereja OS - Multi-tenant Telegram Bot
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class BotConfig:
    """Telegram Bot configuration with multi-tenant support."""
    
    # Bot Token (from environment variable)
    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    
    # Webhook or Polling mode
    # Set WEBHOOK_MODE=true for production (recommended)
    use_webhook: bool = os.getenv("WEBHOOK_MODE", "true").lower() in ("true", "1", "yes")
    
    # Webhook settings
    webhook_host: str = os.getenv("WEBHOOK_HOST", "https://your-domain.com")
    webhook_path: str = os.getenv("WEBHOOK_PATH", "/webhook/telegram")
    webhook_url: Optional[str] = None
    
    # Polling settings (fallback or dev mode)
    polling_interval: int = int(os.getenv("POLLING_INTERVAL", "1"))
    polling_timeout: int = int(os.getenv("POLLING_TIMEOUT", "30"))
    
    # Server settings (for webhook)
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8080"))
    
    # Multi-tenant: Tenant registry (chat_id -> tenant_id)
    # In production, this would be stored in a database
    _tenant_registry: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Build webhook URL after initialization."""
        if self.use_webhook:
            self.webhook_url = f"{self.webhook_host.rstrip('/')}{self.webhook_path}"
    
    def register_tenant(self, chat_id: int, tenant_id: str) -> None:
        """
        Register a chat_id to tenant_id mapping.
        
        Args:
            chat_id: Telegram chat_id
            tenant_id: Unique enterprise/tenant identifier
        """
        self._tenant_registry[chat_id] = tenant_id
    
    def get_tenant_id(self, chat_id: int) -> Optional[str]:
        """
        Get tenant_id by chat_id.
        
        Args:
            chat_id: Telegram chat_id
            
        Returns:
            tenant_id if found, None otherwise
        """
        return self._tenant_registry.get(chat_id)
    
    def load_tenants_from_env(self) -> None:
        """Load tenant mappings from environment variable (TENANT_MAP)."""
        tenant_map_str = os.getenv("TENANT_MAP", "")
        if not tenant_map_str:
            return
        
        # Format: "chat_id1:tenant_id1,chat_id2:tenant_id2"
        for mapping in tenant_map_str.split(","):
            if ":" in mapping:
                chat_id_str, tenant_id = mapping.split(":", 1)
                try:
                    chat_id = int(chat_id_str.strip())
                    self.register_tenant(chat_id, tenant_id.strip())
                except ValueError:
                    pass
    
    @property
    def is_configured(self) -> bool:
        """Check if bot has a valid token."""
        return bool(self.bot_token and self.bot_token != "")


# Global config instance
config = BotConfig()
config.load_tenants_from_env()
