#!/usr/bin/env python3

import os
from app import app, db

def recreate_database():
    """Recreate the database with the correct schema"""
    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            print("✓ Dropped all existing tables")
            
            # Create all tables with current schema
            db.create_all()
            print("✓ Created all tables with current schema")
            
            print("\n✓ Database recreated successfully!")
            print("The application should now work without errors.")
            
        except Exception as e:
            print(f"Error recreating database: {e}")

if __name__ == "__main__":
    recreate_database() 