#!/usr/bin/env python3
"""
Bot Launcher - Avoids event loop conflicts
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def launch_bot():
    """Launch the bot in a clean environment"""
    try:
        # Change to bot directory
        bot_dir = Path(__file__).parent
        os.chdir(bot_dir)
        
        print("🚀 Launching HackReality Bot...")
        print(f"📁 Working directory: {bot_dir}")
        
        # Start bot using subprocess with fresh environment
        env = os.environ.copy()
        env['PYTHONPATH'] = str(bot_dir)
        
        process = subprocess.Popen([
            sys.executable, 'main.py'
        ], 
        cwd=str(bot_dir),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        
        print(f"✅ Bot started with PID: {process.pid}")
        
        # Monitor the process
        try:
            stdout, stderr = process.communicate(timeout=5)
            
            if process.returncode == 0:
                print("✅ Bot started successfully!")
                print("📱 Bot is running and ready to receive messages")
            else:
                print(f"❌ Bot failed to start (exit code: {process.returncode})")
                if stderr:
                    print(f"Error output: {stderr}")
                    
        except subprocess.TimeoutExpired:
            # If it's still running after 5 seconds, it's probably successful
            print("✅ Bot appears to be running successfully!")
            print("📱 Bot is ready to receive messages")
            
            # Keep it running
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping bot...")
                process.terminate()
                process.wait()
                print("✅ Bot stopped")
                
    except Exception as e:
        print(f"❌ Error launching bot: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = launch_bot()
    if not success:
        sys.exit(1)
