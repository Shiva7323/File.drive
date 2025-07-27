#!/usr/bin/env python3

try:
    print("Testing imports...")
    from app import app
    print("✓ App imported successfully")
    
    print("Testing route registration...")
    from register_routes import register_routes
    print("✓ Route registration imported successfully")
    
    print("Testing database...")
    from database import db
    print("✓ Database imported successfully")
    
    print("Testing models...")
    from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion, RecentFile
    print("✓ Models imported successfully")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 