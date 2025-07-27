from app import app, db
from models import Team, TeamMember, User

def test_permissions():
    """Test upload permissions for debugging"""
    with app.app_context():
        # Get all teams
        teams = Team.query.all()
        print(f"Found {len(teams)} teams")
        
        for team in teams:
            print(f"\nTeam: {team.name} (ID: {team.id})")
            print(f"  - Upload mode: {team.upload_permission_mode}")
            print(f"  - Allow editor uploads: {team.allow_editor_uploads}")
            print(f"  - Allow viewer uploads: {team.allow_viewer_uploads}")
            
            # Get team members
            members = TeamMember.query.filter_by(team_id=team.id).all()
            print(f"  - Members: {len(members)}")
            
            for member in members:
                user = User.query.get(member.user_id)
                print(f"    - {user.username}: {member.role}")
                
                # Test upload permission
                from routes import can_upload_file
                can_upload = can_upload_file(team.id, member.user_id)
                print(f"      Can upload: {can_upload}")

if __name__ == "__main__":
    test_permissions() 