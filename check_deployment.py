#!/usr/bin/env python3
"""
Check deployment status for both bots
"""

import requests
import json

def check_github_actions(repo_name):
    """Check GitHub Actions status"""
    url = f"https://api.github.com/repos/DmitryPavl/{repo_name}/actions/runs?per_page=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get('workflow_runs'):
                run = data['workflow_runs'][0]
                return {
                    'status': run.get('status'),
                    'conclusion': run.get('conclusion'),
                    'created_at': run.get('created_at'),
                    'head_sha': run.get('head_sha', '')[:8]
                }
    except Exception as e:
        print(f"Error checking {repo_name}: {e}")
    return None

def check_heroku_app(app_name):
    """Check Heroku app status"""
    try:
        response = requests.get(f"https://{app_name}.herokuapp.com/", timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    print("🚀 Checking deployment status...")
    print()
    
    # Check main bot
    print("📱 Main Bot (HackReality-MainBot):")
    main_actions = check_github_actions("hackreality-main-bot")
    if main_actions:
        print(f"  GitHub Actions: {main_actions['status']} - {main_actions['conclusion']}")
        print(f"  Commit: {main_actions['head_sha']}")
        print(f"  Created: {main_actions['created_at']}")
    else:
        print("  GitHub Actions: Unable to check")
    
    main_heroku = check_heroku_app("hackreality-main-bot")
    print(f"  Heroku App: {'✅ Online' if main_heroku else '❌ Offline'}")
    print()
    
    # Check admin bot
    print("👨‍💼 Admin Bot (HackReality-AdminBot):")
    admin_actions = check_github_actions("hackreality-admin-bot")
    if admin_actions:
        print(f"  GitHub Actions: {admin_actions['status']} - {admin_actions['conclusion']}")
        print(f"  Commit: {admin_actions['head_sha']}")
        print(f"  Created: {admin_actions['created_at']}")
    else:
        print("  GitHub Actions: Unable to check")
    
    admin_heroku = check_heroku_app("hackreality-admin-bot")
    print(f"  Heroku App: {'✅ Online' if admin_heroku else '❌ Offline'}")
    print()
    
    # Summary
    if main_heroku and admin_heroku:
        print("🎉 Both bots are deployed and online!")
    else:
        print("⚠️  Some bots may need attention")

if __name__ == "__main__":
    main()
