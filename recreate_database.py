#!/usr/bin/env python3
"""
Script to recreate the database with correct schema
"""

import os
from database import db
from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion, RecentFile, OAuth

def recreate_database():
    """Recreate the database with all tables"""
    print("Dropping all tables...")
    db.drop_all()
    
    print("Creating all tables...")
    db.create_all()
    
    print("Database recreated successfully!")
    print("All tables created with correct schema.")

if __name__ == "__main__":
    recreate_database() 