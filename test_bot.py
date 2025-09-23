#!/usr/bin/env python3
"""
Minimal test bot to isolate the event loop issue
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    """Handle the /start command"""
    await update.message.reply_text('Hello! Test bot is working!')

async def main():
    """Main function"""
    try:
        token = os.getenv('ADMIN_BOT_TOKEN')  # Use admin bot token for testing
        if not token:
            logger.error("No bot token found")
            return
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Add command handler
        application.add_handler(CommandHandler("start", start_command))
        
        logger.info("Starting test bot...")
        
        # Start the bot
        await application.run_polling()
        
    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
