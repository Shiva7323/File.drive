#!/usr/bin/env python3

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app, db
    
    with app.app_context():
        # Remove existing database file
        db_path = 'instance/filedrive.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✓ Removed existing database: {db_path}")
        
        # Create new database with current schema
        db.create_all()
        print("✓ Created new database with current schema")
        
        print("\n✓ Database reset successful!")
        print("The application should now work without errors.")
        
except Exception as e:
    print(f"Error resetting database: {e}")
    import traceback
    traceback.print_exc() 