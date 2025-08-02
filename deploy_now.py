#!/usr/bin/env python3
"""
Deploy Now - Complete File Drive Deployment
This script will handle the entire deployment process
"""

import os
import subprocess
import webbrowser
import time

def run_command(command):
    """Run a shell command"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def main():
    print("🚀 File Drive - Complete Deployment")
    print("=" * 50)
    
    # Step 1: Check if repository exists
    print("🔍 Checking GitHub repository...")
    success, output, error = run_command("git ls-remote https://github.com/Shiva7323/filedrive.git")
    
    if not success:
        print("❌ Repository not found. Let's create it!")
        print("\n📋 Please follow these steps:")
        print("1. Go to: https://github.com/new")
        print("2. Repository name: filedrive")
        print("3. Description: File Drive - Cloud File Management System")
        print("4. Make it Public ✅")
        print("5. Don't add README ❌")
        print("6. Click 'Create repository'")
        print()
        
        input("Press Enter after creating the repository...")
        
        # Try again
        success, output, error = run_command("git ls-remote https://github.com/Shiva7323/filedrive.git")
        if not success:
            print("❌ Repository still not found. Please check the URL and try again.")
            return
    
    print("✅ Repository found!")
    
    # Step 2: Set up remote and push
    print("\n📡 Setting up Git remote...")
    success, output, error = run_command('git remote set-url origin https://github.com/Shiva7323/filedrive.git')
    if not success:
        print(f"❌ Error setting remote: {error}")
        return
    
    print("📤 Pushing code to GitHub...")
    success, output, error = run_command("git push -u origin main")
    if not success:
        print(f"❌ Error pushing to GitHub: {error}")
        return
    
    print("✅ Code pushed to GitHub successfully!")
    
    # Step 3: Deploy to Railway
    print("\n🚀 Deploying to Railway...")
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