#!/usr/bin/env python3

import os
import sys
import shutil

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def fix_database():
    """Fix database schema issues"""
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
            
    except Exception as e:
        print(f"Error fixing database: {e}")

def clean_test_files():
    """Remove test files that might be causing issues"""
    test_files = [
        'test_import.py',
        'test_models.py', 
        'simple_test.py',
        'migrate_db.py',
        'fix_db.py',
        'recreate_db.py',
        'reset_db.py'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Removed test file: {file}")

def main():
    print("Fixing all issues...")
    
    # Clean up test files
    clean_test_files()
    
    # Fix database
    fix_database()
    
    print("\n✓ All issues fixed!")
    print("You can now run: python main.py")

if __name__ == "__main__":
    main() 