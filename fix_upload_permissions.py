from app import app, db
from models import Team, TeamMember

def fix_upload_permissions():
    """Fix upload permissions for existing teams"""
    with app.app_context():
        # Get all teams
        teams = Team.query.all()
        
        for team in teams:
            print(f"Processing team: {team.name}")
            
            # Set default upload permission mode if not set
            if not hasattr(team, 'upload_permission_mode') or team.upload_permission_mode is None:
                team.upload_permission_mode = 'role_based'
                print(f"  - Set upload_permission_mode to 'role_based'")
            
            # Set default editor upload permission if not set
            if not hasattr(team, 'allow_editor_uploads') or team.allow_editor_uploads is None:
                team.allow_editor_uploads = True
                print(f"  - Set allow_editor_uploads to True")
            
            # Set default viewer upload permission if not set
            if not hasattr(team, 'allow_viewer_uploads') or team.allow_viewer_uploads is None:
                team.allow_viewer_uploads = False
                print(f"  - Set allow_viewer_uploads to False")
            
            # Check if team creator is admin
            creator_membership = TeamMember.query.filter(
                TeamMember.team_id == team.id,
                TeamMember.user_id == team.created_by
            ).first()
            
            if creator_membership and creator_membership.role != 'admin':
                creator_membership.role = 'admin'
                print(f"  - Set team creator role to 'admin'")
        
        # Commit changes
        db.session.commit()
        print("Upload permissions fixed successfully!")

if __name__ == "__main__":
    fix_upload_permissions() 