"""
MeshTradeBot Telegram Bot Handler (aiogram 3.x)

Main bot initialization and startup logic.
Contains:
- FSMContext for user states
- Router setup
- Middleware configuration
- Webhook setup (for both Telegram and Freqtrade)
- Error handling

Status: Phase 2 of development
"""

import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pathlib import Path

# Import handlers
from .handlers import router
from database import init_db
from utils.logger import setup_logging

logger = setup_logging(__name__, "./logs/bot.log")


class MeshTradeBot:
    """Main bot class handling initialization and startup"""

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        # Initialize bot with default properties
        self.bot = Bot(
            token=self.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        # Use memory storage for FSM (can be changed to Redis later)
        storage = MemoryStorage()

        # Initialize dispatcher
        self.dp = Dispatcher(storage=storage)

        # Register routers
        self.dp.include_router(router)

        # Setup middleware and error handlers
        self._setup_middleware()
        self._setup_error_handlers()

        # Webhook settings
        self.webhook_host = os.getenv("WEBHOOK_HOST", "0.0.0.0")
        self.webhook_port = int(os.getenv("WEBHOOK_PORT", "8433"))
        self.webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
        self.webhook_url = os.getenv("WEBHOOK_URL")  # Full URL for webhook

    def _setup_middleware(self):
        """Setup middleware for rate limiting, logging, etc."""
        # TODO: Add rate limiting middleware in Phase 2
        # TODO: Add logging middleware
        pass

    def _setup_error_handlers(self):
        """Setup global error handlers"""
        @self.dp.errors()
        async def handle_error(update, exception):
            logger.error(f"Unhandled error: {exception}", exc_info=True)
            # TODO: Send error message to admin user
            return True

    async def start_polling(self):
        """Start bot with polling (for development)"""
        logger.info("🤖 Starting MeshTradeBot with polling...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise

    async def start_webhook(self):
        """Start bot with webhook (for production)"""
        logger.info(f"🤖 Starting MeshTradeBot with webhook on port {self.webhook_port}...")

        # Create aiohttp app
        app = web.Application()

        # Setup webhook
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=self.dp,
            bot=self.bot,
            secret_token=os.getenv("WEBHOOK_SECRET")
        )

        webhook_requests_handler.register(app, path=self.webhook_path)

        # Setup additional routes (Freqtrade webhook, health check)
        app.router.add_get("/health", self._health_check)
        app.router.add_post("/freqtrade/webhook", self._freqtrade_webhook)

        # Set webhook URL if provided
        if self.webhook_url:
            await self.bot.set_webhook(
                url=f"{self.webhook_url}{self.webhook_path}",
                secret_token=os.getenv("WEBHOOK_SECRET")
            )
            logger.info(f"✓ Webhook set to: {self.webhook_url}{self.webhook_path}")

        # Start server
        try:
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.webhook_host, self.webhook_port)
            await site.start()
            logger.info(f"✓ Webhook server started on {self.webhook_host}:{self.webhook_port}")

            # Keep the server running
            await asyncio.Event().wait()
        except Exception as e:
            logger.error(f"Error starting webhook server: {e}")
            raise
        finally:
            if self.webhook_url:
                await self.bot.delete_webhook()
            logger.info("✓ Webhook deleted")

    async def _health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "bot": "MeshTradeBot"})

    async def _freqtrade_webhook(self, request):
        """Handle Freqtrade webhook signals (to be implemented in Phase 4)"""
        # TODO: Implement Freqtrade signal processing
        logger.info("📡 Freqtrade webhook received (not implemented yet)")
        return web.json_response({"status": "received"})

    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down MeshTradeBot...")
        await self.bot.session.close()
        logger.info("✓ Bot shutdown complete")


async def main():
    """Main entry point"""
    # Initialize database
    init_db()

    # Create bot instance
    bot_instance = MeshTradeBot()

    try:
        # Choose polling or webhook based on environment
        use_webhook = os.getenv("USE_WEBHOOK", "false").lower() == "true"

        if use_webhook:
            await bot_instance.start_webhook()
        else:
            await bot_instance.start_polling()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise
    finally:
        await bot_instance.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
