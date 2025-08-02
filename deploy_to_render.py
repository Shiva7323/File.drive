#!/usr/bin/env python3
"""
Deploy File Drive to Render
A simple script to help deploy the application to Render's free hosting platform.
"""

import webbrowser
import os
import sys

def main():
    print("🚀 File Drive - Render Deployment")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    print("✅ Project files found!")
    print("\n📋 Deployment Steps:")
    print("1. Push latest changes to GitHub")
    print("2. Open Render dashboard")
    print("3. Connect your GitHub repository")
    print("4. Deploy automatically")
    
    # Push to GitHub first
    print("\n🔄 Pushing to GitHub...")
    os.system("git add .")
    os.system('git commit -m "Prepare for Render deployment"')
    os.system("git push origin main")
    
    print("\n✅ Code pushed to GitHub!")
    
    # Open Render
    print("\n🌐 Opening Render dashboard...")
    render_url = "https://render.com/new/web-service"
    webbrowser.open(render_url)
    
    print("\n📝 Manual Steps:")
    print("1. Click 'Connect' next to your GitHub repository")
    print("2. Select the 'File.drive' repository")
    print("3. Configure the service:")
    print("   - Name: filedrive (or any name you prefer)")
    print("   - Environment: Python")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn main:application")
    print("4. Click 'Create Web Service'")
    print("5. Wait for deployment (2-3 minutes)")
    
    print("\n🎉 Your File Drive will be live at: https://your-app-name.onrender.com")
    print("\n💡 Tips:")
    print("- Render's free tier includes 750 hours/month")
    print("- Your app will sleep after 15 minutes of inactivity")
    print("- First request after sleep may take 30-60 seconds")
    print("- You can upgrade to paid plan for always-on service")

if __name__ == "__main__":
    main() 