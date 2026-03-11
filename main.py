"""
MeshTradeBot - Main Entry Point

This is the main application runner for the Telegram trading bot.
Initializes all components and starts the bot.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Import project modules
from database import init_db
from utils.logger import setup_logging
from config.constants import RISK_DISCLAIMER

logger = setup_logging(__name__, "./logs/meshtradebot.log")


async def initialize_bot():
    """
    Initialize all bot components.
    This is called on startup before the bot starts polling.
    """
    logger.info("🤖 MeshTradeBot starting up...")
    
    # Check environment variables
    required_env_vars = [
        "TELEGRAM_BOT_TOKEN",
        "ENCRYPTION_KEY",
    ]
    
    for var in required_env_vars:
        if not os.getenv(var):
            logger.error(f"❌ Missing environment variable: {var}")
            raise ValueError(f"Missing required environment variable: {var}")
    
    logger.info("✓ Environment variables validated")
    
    # Initialize database
    try:
        init_db()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Print startup information
    logger.info(RISK_DISCLAIMER)
    logger.info("✓ All systems initialized")


async def main():
    """Main bot entry point"""
    try:
        # Initialize
        await initialize_bot()
        
        # Import bot after initialization
        # This will be created in the next step
        logger.info("📱 Bot module initialization...")
        try:
            from bot.main import start_bot
            await start_bot()
        except ImportError:
            logger.warning("⚠️  Bot module not yet implemented. Waiting for bot/main.py...")
            logger.info("Current components initialized:")
            logger.info("  ✓ Database models & ORM")
            logger.info("  ✓ Encryption utilities")
            logger.info("  ✓ Configuration & constants")
            logger.info("  ✓ Logging")
            logger.info("  ✓ Freqtrade strategy")
            logger.info("  ✓ Environment setup")
            
            logger.info("\nNext steps:")
            logger.info("  1. Create bot/main.py with aiogram bot handler")
            logger.info("  2. Create bot/handlers/ with command handlers")
            logger.info("  3. Create bot/keyboards/ with button layouts")
            logger.info("  4. Create bot/payments/ with Telegram Payments logic")
            
            logger.info("\nFor now, database is running. Test with:")
            logger.info("  python -c \"from database import get_db_context; "
                       "from database.models import User; "
                       "db = get_db_context().__enter__(); "
                       "print(db.query(User).count())\"")
            
            # Keep running for monitoring
            await asyncio.sleep(3600)
    
    except Exception as e:
        logger.critical(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️  Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)
