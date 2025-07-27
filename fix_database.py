import os
import sqlite3
from app import app, db
from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion

def fix_database():
    """Fix the database schema by recreating it"""
    
    # Delete the database file if it exists
    db_path = os.path.join(app.instance_path, 'app.db')
    if os.path.exists(db_path):
        print(f"Deleting existing database: {db_path}")
        os.remove(db_path)
    
    # Create the database with new schema
    with app.app_context():
        print("Creating new database with updated schema...")
        db.create_all()
        print("Database created successfully!")
        
        # Test creating a user with empty email
        try:
            test_user = User.create_user(
                username="testuser",
                password="testpassword123",
                email="",  # Empty email should be stored as None
                first_name="Test",
                last_name="User"
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully with empty email")
            
            # Clean up test user
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Test user cleaned up")
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            db.session.rollback()

if __name__ == "__main__":
    fix_database() 