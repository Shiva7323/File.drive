#!/usr/bin/env python3

try:
    from app import app
    print("✓ App imported successfully")
    
    from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion, RecentFile
    print("✓ All models imported successfully")
    
    # Test creating a User instance
    user = User()
    print("✓ User model instantiated successfully")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 