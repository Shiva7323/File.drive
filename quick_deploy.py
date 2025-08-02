#!/usr/bin/env python3
"""
Quick Deploy Script for File Drive to Railway
This script will automatically:
1. Set up the GitHub repository
2. Push the code
3. Deploy to Railway
"""

import os
import subprocess
import webbrowser
import time
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def get_github_username():
    """Get GitHub username"""
    username = run_command("git config user.name", check=False)
    if not username:
        username = input("Enter your GitHub username: ").strip()
    return username

def setup_github_repo(username):
    """Set up GitHub repository"""
    print(f"🔧 Setting up GitHub repository for: {username}")
    
    # Set remote URL
    remote_url = f"https://github.com/{username}/filedrive.git"
    print(f"📡 Setting remote URL: {remote_url}")
    
    result = run_command(f'git remote set-url origin "{remote_url}"')
    if not result:
        print("❌ Failed to set remote URL")
        return False
    
    # Push to GitHub
    print("📤 Pushing code to GitHub...")
    result = run_command("git push -u origin main")
    if not result:
        print("❌ Failed to push to GitHub")
        print("💡 Make sure you've created the repository at: https://github.com/new")
        print("   Repository name: filedrive")
        print("   Make it Public ✅")
        return False
    
    print("✅ Code pushed to GitHub successfully!")
    return True

def deploy_to_railway():
    """Deploy to Railway"""
    print("🚀 Deploying to Railway...")
    
    # Open Railway in browser
    railway_url = "https://railway.app/new"
    print(f"🌐 Opening Railway: {railway_url}")
    webbrowser.open(railway_url)
    
    print("\n📋 Railway Deployment Steps:")
    print("1. Sign up/Login with GitHub")
    print("2. Click 'New Project'")
    print("3. Select 'Deploy from GitHub repo'")
    print("4. Choose your 'filedrive' repository")
    print("5. Railway will auto-detect Python app")
    print("6. Click 'Deploy'")
    print()
    
    input("Press Enter after deploying to Railway...")
    return True

def main():
    """Main deployment process"""
    print("🚀 File Drive - Quick Deployment to Railway")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run this script from the project directory.")
        return
    
    # Get GitHub username
    username = get_github_username()
    print(f"👤 GitHub username: {username}")
    
    # Setup GitHub repository
    if not setup_github_repo(username):
        print("\n🔧 Manual GitHub Setup Required:")
        print(f"1. Go to: https://github.com/new")
        print(f"2. Repository name: filedrive")
        print(f"3. Make it Public ✅")
        print(f"4. Don't add README ❌")
        print(f"5. Click 'Create repository'")
        print(f"6. Run this script again")
        return
    
    # Deploy to Railway
    if not deploy_to_railway():
        print("❌ Failed to deploy to Railway")
        return
    
    print("\n🎉 Deployment process completed!")
    print("=" * 50)
    print("📱 Your File Drive will be live at:")
    print("   https://filedrive-production.up.railway.app")
    print("   https://filedrive-production.up.railway.app/mobile")
    print()
    print("🔧 Next steps:")
    print("1. Wait for Railway to finish building (2-5 minutes)")
    print("2. Check the deployment logs in Railway dashboard")
    print("3. Test your live application")
    print("4. Share the URL with others!")

if __name__ == "__main__":
    main() 