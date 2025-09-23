#!/usr/bin/env python3
"""
Heroku-compatible main bot launcher
"""

import os
import sys
import logging
import asyncio
from telegram.ext import Application

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging for Heroku
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_bot():
    """Start the bot with proper event loop handling"""
    try:
        logger.info("Starting HackReality Bot on Heroku...")
        
        # Import here to avoid circular imports
        from main import TelegramBot
        
        # Create bot instance
        bot = TelegramBot()
        
        # Get the application directly
        app = bot.application
        
        # Start polling
        logger.info("Starting bot polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        logger.info("Bot is running and polling...")
        
        # Keep running
        try:
            # Wait indefinitely
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

def main():
    """Main function for Heroku deployment"""
    try:
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(start_bot())
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()