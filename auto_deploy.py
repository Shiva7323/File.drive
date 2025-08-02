#!/usr/bin/env python3
"""
Auto Deploy Script for File Drive to Railway
This script will:
1. Create a GitHub repository
2. Push the code
3. Deploy to Railway
"""

import os
import subprocess
import requests
import json
import time
import webbrowser
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Error running: {command}")
            print(f"Error: {result.stderr}")
            return False
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Exception running: {command}")
        print(f"Error: {e}")
        return False

def get_github_username():
    """Get GitHub username from git config"""
    username = run_command("git config user.name", check=False)
    if not username:
        username = input("Enter your GitHub username: ").strip()
    return username

def create_github_repo(username, repo_name="filedrive"):
    """Create GitHub repository using GitHub CLI or manual instructions"""
    print(f"🔧 Creating GitHub repository: {username}/{repo_name}")
    
    # Try using GitHub CLI if available
    gh_cli_result = run_command("gh --version", check=False)
    if gh_cli_result:
        print("✅ GitHub CLI found, creating repository...")
        result = run_command(f'gh repo create {repo_name} --public --description "File Drive - Cloud File Management System" --source=. --remote=origin --push')
        if result:
            print("✅ GitHub repository created successfully!")
            return True
    
    # Manual instructions if GitHub CLI not available
    print("📋 Manual GitHub repository creation required:")
    print(f"1. Go to: https://github.com/new")
    print(f"2. Repository name: {repo_name}")
    print(f"3. Make it Public ✅")
    print(f"4. Don't add README ❌")
    print(f"5. Click 'Create repository'")
    print()
    
    input("Press Enter after creating the repository...")
    return True

def setup_git_remote(username, repo_name="filedrive"):
    """Set up git remote and push code"""
    print("🔧 Setting up Git remote...")
    
    # Set remote URL
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    result = run_command(f'git remote set-url origin "{remote_url}"')
    if not result:
        print(f"❌ Failed to set remote URL")
        return False
    
    # Push to GitHub
    print("📤 Pushing code to GitHub...")
    result = run_command("git push -u origin main")
    if not result:
        print("❌ Failed to push to GitHub")
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
    
    print("📋 Railway Deployment Steps:")
    print("1. Sign up/Login with GitHub")
    print("2. Click 'New Project'")
    print("3. Select 'Deploy from GitHub repo'")
    print("4. Choose your 'filedrive' repository")
    print("5. Railway will auto-detect Python app")
    print("6. Click 'Deploy'")
    print()
    
    # Wait for user to complete deployment
    input("Press Enter after deploying to Railway...")
    
    print("✅ Railway deployment initiated!")
    return True

def main():
    """Main deployment process"""
    print("🚀 File Drive - Auto Deployment to Railway")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Error: main.py not found. Please run this script from the project directory.")
        return
    
    # Get GitHub username
    username = get_github_username()
    print(f"👤 GitHub username: {username}")
    
    # Create GitHub repository
    if not create_github_repo(username):
        print("❌ Failed to create GitHub repository")
        return
    
    # Setup git remote and push
    if not setup_git_remote(username):
        print("❌ Failed to setup git remote")
        return
    
    # Deploy to Railway
    if not deploy_to_railway():
        print("❌ Failed to deploy to Railway")
        return
    
    print("🎉 Deployment process completed!")
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