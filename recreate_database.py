#!/usr/bin/env python3
"""
Script to recreate the database with correct schema
"""

from app import app, db
import os

def recreate_database():
    """Drop and recreate the database with updated schema"""
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables with updated schema
        print("Creating tables with updated schema...")
        db.create_all()
        
        print("Database recreated successfully!")
        print("The team_id field in the files table is now nullable for single users.")

if __name__ == "__main__":
    recreate_database() 