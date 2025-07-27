#!/usr/bin/env python3

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        # Remove existing database file if it exists
        db_path = 'instance/filedrive.db'
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✓ Removed existing database: {db_path}")
        
        # Import and run the application
        from app import app, db
        
        with app.app_context():
            # Create new database with current schema
            db.create_all()
            print("✓ Created new database with current schema")
        
        print("✓ Starting application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 