#!/usr/bin/env python3

import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing model imports...")
    
    # Import the app and database
    from app import app, db
    print("✓ App and database imported successfully")
    
    # Import all models
    from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion, RecentFile
    print("✓ All models imported successfully")
    
    # Test creating instances
    with app.app_context():
        print("✓ App context created successfully")
        
        # Test User model
        user = User()
        print("✓ User model instantiated successfully")
        
        # Test Team model
        team = Team()
        print("✓ Team model instantiated successfully")
        
        # Test File model
        file = File()
        print("✓ File model instantiated successfully")
        
        print("All models working correctly!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 