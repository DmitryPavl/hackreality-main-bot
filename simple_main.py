#!/usr/bin/env python3
"""
Simple Main Bot Launcher
Avoids event loop conflicts by using a clean approach
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function"""
    try:
        # Import here to avoid circular imports
        from main import TelegramBot
        
        logger.info("Creating bot instance...")
        bot = TelegramBot()
        
        logger.info("Starting bot...")
        await bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")

if __name__ == "__main__":
    # Use a fresh event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        loop.close()
