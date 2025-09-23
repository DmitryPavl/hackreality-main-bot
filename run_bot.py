#!/usr/bin/env python3
"""
Bot runner using multiprocessing to avoid event loop conflicts
"""

import os
import sys
import multiprocessing
import time
from pathlib import Path

def run_admin_bot():
    """Run admin bot in a separate process"""
    try:
        # Change to bot directory
        bot_dir = Path(__file__).parent
        os.chdir(bot_dir)
        
        # Import and run the admin bot
        from admin_bot_complete import CompleteAdminBot
        import asyncio
        
        async def main():
            bot = CompleteAdminBot()
            await bot.run()
        
        # Run in a fresh event loop
        asyncio.run(main())
        
    except Exception as e:
        print(f"Admin bot error: {e}")

def run_main_bot():
    """Run main bot in a separate process"""
    try:
        # Change to bot directory
        bot_dir = Path(__file__).parent
        os.chdir(bot_dir)
        
        # Import and run the main bot
        from main import TelegramBot
        import asyncio
        
        async def main():
            bot = TelegramBot()
            await bot.run()
        
        # Run in a fresh event loop
        asyncio.run(main())
        
    except Exception as e:
        print(f"Main bot error: {e}")

def main():
    """Main function to start bots"""
    print("🚀 Starting bots using multiprocessing...")
    
    # Start admin bot in a separate process
    admin_process = multiprocessing.Process(target=run_admin_bot, name="AdminBot")
    admin_process.start()
    print(f"✅ Admin bot started with PID: {admin_process.pid}")
    
    # Start main bot in a separate process
    main_process = multiprocessing.Process(target=run_main_bot, name="MainBot")
    main_process.start()
    print(f"✅ Main bot started with PID: {main_process.pid}")
    
    print("🎉 Both bots are running!")
    print("Press Ctrl+C to stop all bots")
    
    try:
        # Wait for both processes
        admin_process.join()
        main_process.join()
    except KeyboardInterrupt:
        print("\n🛑 Stopping bots...")
        admin_process.terminate()
        main_process.terminate()
        admin_process.join()
        main_process.join()
        print("✅ All bots stopped")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)
    main()
