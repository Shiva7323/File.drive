#!/usr/bin/env python3

from app import app, db
from sqlalchemy import text

def fix_database():
    """Add missing columns to existing database"""
    with app.app_context():
        try:
            # Add missing columns to users table
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN use_single_user_mode BOOLEAN DEFAULT FALSE
            """))
            print("✓ Added use_single_user_mode column to users table")
        except Exception as e:
            print(f"Note: use_single_user_mode column might already exist: {e}")
        
        try:
            # Add missing columns to teams table
            db.session.execute(text("""
                ALTER TABLE teams 
                ADD COLUMN group_photo_url VARCHAR(500)
            """))
            print("✓ Added group_photo_url column to teams table")
        except Exception as e:
            print(f"Note: group_photo_url column might already exist: {e}")
        
        try:
            db.session.execute(text("""
                ALTER TABLE teams 
                ADD COLUMN bin_retention_days INTEGER DEFAULT 30
            """))
            print("✓ Added bin_retention_days column to teams table")
        except Exception as e:
            print(f"Note: bin_retention_days column might already exist: {e}")
        
        try:
            db.session.execute(text("""
                ALTER TABLE teams 
                ADD COLUMN only_admin_can_restore BOOLEAN DEFAULT TRUE
            """))
            print("✓ Added only_admin_can_restore column to teams table")
        except Exception as e:
            print(f"Note: only_admin_can_restore column might already exist: {e}")
        
        try:
            # Add missing columns to files table
            db.session.execute(text("""
                ALTER TABLE files 
                ADD COLUMN is_in_bin BOOLEAN DEFAULT FALSE
            """))
            print("✓ Added is_in_bin column to files table")
        except Exception as e:
            print(f"Note: is_in_bin column might already exist: {e}")
        
        try:
            db.session.execute(text("""
                ALTER TABLE files 
                ADD COLUMN bin_expiry_date DATETIME
            """))
            print("✓ Added bin_expiry_date column to files table")
        except Exception as e:
            print(f"Note: bin_expiry_date column might already exist: {e}")
        
        try:
            db.session.execute(text("""
                ALTER TABLE files 
                ADD COLUMN deleted_by VARCHAR
            """))
            print("✓ Added deleted_by column to files table")
        except Exception as e:
            print(f"Note: deleted_by column might already exist: {e}")
        
        # Commit all changes
        db.session.commit()
        
        print("\n✓ Database migration completed successfully!")
        print("The application should now work without errors.")

if __name__ == "__main__":
    fix_database() 