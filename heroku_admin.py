#!/usr/bin/env python3
"""
Heroku-compatible admin bot launcher
"""

import os
import sys
import logging

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from admin_bot_complete import CompleteAdminBot

# Configure logging for Heroku
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function for Heroku deployment"""
    try:
        logger.info("Starting HackReality Admin Bot on Heroku...")
        bot = CompleteAdminBot()
        bot.run()
    except Exception as e:
        logger.error(f"Failed to start admin bot: {e}")
        raise

if __name__ == "__main__":
    main()
