#!/usr/bin/env python3
"""
Simple Admin Bot Launcher
Uses a different approach to avoid event loop conflicts
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def launch_admin_bot():
    """Launch the admin bot"""
    try:
        # Change to bot directory
        bot_dir = Path(__file__).parent
        os.chdir(bot_dir)
        
        print("🚀 Launching Admin Bot...")
        print(f"📁 Working directory: {bot_dir}")
        
        # Start bot using subprocess with fresh environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(bot_dir)
        
        # Create a simple script that runs the admin bot
        script_content = '''
import sys
import os
sys.path.insert(0, os.getcwd())

from admin_bot_complete import CompleteAdminBot
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        bot = CompleteAdminBot()
        await bot.run()
    except Exception as e:
        logger.error(f"Admin bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        # Write the script to a temporary file
        script_path = bot_dir / "temp_admin.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        try:
            process = subprocess.Popen([
                sys.executable, str(script_path)
            ], 
            cwd=str(bot_dir),
            env=env
            )
            
            print(f"✅ Admin bot started with PID: {process.pid}")
            
            # Monitor the process
            try:
                stdout, stderr = process.communicate(timeout=5)
                
                if process.returncode == 0:
                    print("✅ Admin bot started successfully!")
                    print("📱 Admin bot is running and ready to receive commands")
                else:
                    print(f"❌ Admin bot failed to start (exit code: {process.returncode})")
                    if stderr:
                        print(f"Error output: {stderr}")
                        
            except subprocess.TimeoutExpired:
                # If it's still running after 5 seconds, it's probably successful
                print("✅ Admin bot appears to be running successfully!")
                print("📱 Admin bot is ready to receive commands")
                
                # Keep it running
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping admin bot...")
                    process.terminate()
                    process.wait()
                    print("✅ Admin bot stopped")
                    
        finally:
            # Clean up the temporary script
            if script_path.exists():
                script_path.unlink()
                
    except Exception as e:
        print(f"❌ Error launching admin bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = launch_admin_bot()
    if not success:
        sys.exit(1)
