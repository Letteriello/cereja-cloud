"""
Telegram Bot Main - Cereja OS
Multi-tenant bot using aiogram v3

Webhook endpoint: POST /webhook/telegram
"""

import asyncio
import logging
import os
import sys
from typing import Optional

import aiogram
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, Update
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp import AiohttpWebhookHandler

from bot_config import config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Bot and Dispatcher instances
bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Router for handlers
router = Router()


# ─────────────────────────────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command - Welcome message."""
    tenant_id = config.get_tenant_id(message.chat.id)
    tenant_info = f" [Tenant: {tenant_id}]" if tenant_id else ""
    
    welcome_text = (
        "🍒 <b>Cereja OS Bot</b>\n\n"
        "Bem-vindo ao Cereja OS!\n"
        "Estou aqui para ajudar a gerenciar suas tarefas e operações.\n\n"
        f"<b>Chat ID:</b> <code>{message.chat.id}</code>\n"
        f"<b>Tenant:</b> <code>{tenant_id or 'Não registrado'}</code>\n\n"
        "Use /help para ver os comandos disponíveis."
    )
    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command - Show help message."""
    help_text = (
        "📖 <b>Comandos Disponíveis</b>\n\n"
        "• <code>/start</code> - Iniciar o bot\n"
        "• <code>/help</code> - Mostrar esta ajuda\n"
        "• <code>/status &lt;task_id&gt;</code> - Verificar status de uma tarefa\n"
        "• <code>/ping</code> - Testar conexão\n\n"
        "<b>Outras ações:</b>\n"
        "• Envie qualquer mensagem de texto para ser direcionada ao Orquestrador\n"
    )
    await message.answer(help_text)


@router.message(Command("ping"))
async def cmd_ping(message: Message) -> None:
    """Handle /ping command - Connection test."""
    await message.answer("🏓 <b>Pong!</b> Bot está funcionando.")


@router.message(F.text.regexp(r"^/status(?:\s+(.+))?$"))
async def cmd_status(message: Message, status_text: Optional[str] = None) -> None:
    """
    Handle /status <task_id> - Query task status.
    
    Forwards the task_id query to Orquestrador service.
    """
    if not status_text:
        await message.answer(
            "⚠️ <b>Uso:</b> <code>/status &lt;task_id&gt;</code>\n"
            "Exemplo: <code>/status TSK-12345</code>"
        )
        return
    
    tenant_id = config.get_tenant_id(message.chat.id)
    logger.info(f"Status query for task_id={status_text}, tenant={tenant_id}, chat_id={message.chat.id}")
    
    # TODO: Integrate with Orquestrador API
    # For now, return a placeholder response
    await message.answer(
        f"🔍 <b>Consultando status da tarefa:</b> <code>{status_text}</code>\n\n"
        f"Tenant: <code>{tenant_id or 'N/A'}</code>\n"
        "⏳ Integracja com Orquestrador em desenvolvimento..."
    )


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """
    Handle plain text messages.
    Forwards to Orquestrador for processing.
    """
    tenant_id = config.get_tenant_id(message.chat.id)
    
    logger.info(
        f"Text message from chat_id={message.chat.id}, "
        f"tenant={tenant_id}, text={message.text[:50]}..."
    )
    
    # TODO: Forward to Orquestrador API
    # Example: await orquestrador_client.forward_message(...)
    
    await message.answer(
        "📨 <b>Mensagem recebida</b>\n\n"
        f"Sua mensagem foi direcionada ao Orquestrador.\n"
        f"Tenant: <code>{tenant_id or 'N/A'}</code>\n"
        "⏳ Processing..."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Webhook Setup (Production)
# ─────────────────────────────────────────────────────────────────────────────

async def on_startup() -> None:
    """Run on bot startup."""
    logger.info("Bot starting up...")
    
    if config.use_webhook and config.webhook_url:
        logger.info(f"Setting webhook to: {config.webhook_url}")
        await bot.set_webhook(
            url=config.webhook_url,
            drop_pending_updates=True
        )
        logger.info("Webhook configured successfully")
    else:
        logger.info("Starting in polling mode (not recommended for production)")


async def on_shutdown() -> None:
    """Run on bot shutdown."""
    logger.info("Bot shutting down...")
    await bot.delete_webhook()
    await bot.session.close()


# ─────────────────────────────────────────────────────────────────────────────
# Webhook Handler (for aiohttp server)
# ─────────────────────────────────────────────────────────────────────────────

class WebhookHandler(AiohttpWebhookHandler):
    """Custom webhook handler with startup/shutdown hooks."""
    
    async def on_startup(self, webhook_ip: Optional[str] = None) -> None:
        await on_startup()
    
    async def on_shutdown(self) -> None:
        await on_shutdown()


# ─────────────────────────────────────────────────────────────────────────────
# Polling Mode (Development)
# ─────────────────────────────────────────────────────────────────────────────

async def run_polling() -> None:
    """Run bot in polling mode (development only)."""
    logger.info("Starting polling mode...")
    await on_startup()
    await dp.start_polling(bot)


# ─────────────────────────────────────────────────────────────────────────────
# Webhook Server Mode (Production)
# ─────────────────────────────────────────────────────────────────────────────

async def run_webhook_server() -> None:
    """Run bot with webhook on aiohttp server."""
    from aiohttp import web
    
    logger.info(f"Starting webhook server on {config.server_host}:{config.server_port}")
    
    handler = WebhookHandler(
        dispatcher=dp,
        bot=bot,
        webhook_path=config.webhook_path.lstrip("/")
    )
    
    app = web.Application()
    handler.register(app, path=config.webhook_path)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, config.server_host, config.server_port)
    await site.start()
    
    logger.info(f"Webhook server started at {config.webhook_url}")
    
    # Keep the server running
    await asyncio.Event().wait()


# ─────────────────────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    """Main entry point."""
    # Include router
    dp.include_router(router)
    
    # Set up middlewares if needed
    # from aiogram.dispatcher.flags import get_flag
    # dp.message.middleware(SomeMiddleware())
    
    if config.use_webhook:
        await run_webhook_server()
    else:
        await run_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
        sys.exit(1)
