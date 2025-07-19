import os
import secrets
import uuid
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask import session, render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from flask_login import current_user
from sqlalchemy import or_

from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True

def log_activity(team_id, action, target_type=None, target_id=None, description=None):
    """Helper function to log team activities"""
    if current_user.is_authenticated:
        activity = Activity(
            team_id=team_id,
            user_id=current_user.id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description
        )
        db.session.add(activity)
        db.session.commit()

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    allowed_extensions = {'txt', 'md', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'pdf', 'svg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_type(filename):
    """Determine file type category"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'svg']:
        return 'image'
    elif ext in ['txt', 'md']:
        return 'text'
    elif ext in ['docx', 'pdf']:
        return 'document'
    else:
        return 'other'

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/demo')
def demo_dashboard():
    """Demo route to showcase the UI without authentication"""
    # Create demo data for showcase
    demo_files = [
        {'id': 1, 'original_filename': 'project-notes.md', 'file_type': 'text', 'file_size': 2048, 'updated_at': datetime.now(), 'uploader': {'display_name': 'Demo User'}},
        {'id': 2, 'original_filename': 'team-photo.jpg', 'file_type': 'image', 'file_size': 1024000, 'updated_at': datetime.now(), 'uploader': {'display_name': 'Demo User'}},
        {'id': 3, 'original_filename': 'presentation.pdf', 'file_type': 'document', 'file_size': 512000, 'updated_at': datetime.now(), 'uploader': {'display_name': 'Demo User'}}
    ]
    
    demo_messages = [
        {'id': 1, 'content': 'Welcome to File Drive! This is a demo of our collaboration platform.', 'created_at': datetime.now(), 'sender': {'display_name': 'Demo User', 'profile_image_url': None}},
        {'id': 2, 'content': 'You can upload files, chat with team members, and collaborate in real-time.', 'created_at': datetime.now(), 'sender': {'display_name': 'Team Lead', 'profile_image_url': None}}
    ]
    
    demo_activities = [
        {'id': 1, 'description': 'Demo User uploaded project-notes.md', 'created_at': datetime.now()},
        {'id': 2, 'description': 'Team Lead sent a message in the chat', 'created_at': datetime.now()}
    ]
    
    demo_team_members = [
        ({'id': '1', 'display_name': 'Demo User', 'profile_image_url': None}, 'admin'),
        ({'id': '2', 'display_name': 'Team Lead', 'profile_image_url': None}, 'editor'),
        ({'id': '3', 'display_name': 'Collaborator', 'profile_image_url': None}, 'viewer')
    ]
    
    demo_team = {
        'id': 1,
        'name': 'Demo Team',
        'description': 'A demonstration team showcasing File Drive features',
        'invite_code': 'DEMO123'
    }
    
    return render_template('dashboard.html',
                         user_teams=[demo_team],
                         current_team=demo_team,
                         recent_files=demo_files,
                         team_messages=demo_messages,
                         team_activities=demo_activities,
                         team_members=demo_team_members)

@app.route('/dashboard')
@require_login
def dashboard():
    # Get user's teams
    user_teams = db.session.query(Team).join(TeamMember).filter(
        TeamMember.user_id == current_user.id
    ).all()
    
    # Get current team from session or first team
    current_team_id = session.get('current_team_id')
    current_team = None
    
    if current_team_id:
        current_team = next((t for t in user_teams if t.id == current_team_id), None)
    
    if not current_team and user_teams:
        current_team = user_teams[0]
        session['current_team_id'] = current_team.id
    
    # Get team data if user has a team
    recent_files = []
    team_messages = []
    team_activities = []
    team_members = []
    
    if current_team:
        # Get recent files
        recent_files = File.query.filter(
            File.team_id == current_team.id,
            File.is_deleted == False
        ).order_by(File.updated_at.desc()).limit(10).all()
        
        # Get recent messages
        team_messages = Message.query.filter(
            Message.team_id == current_team.id
        ).order_by(Message.created_at.desc()).limit(20).all()
        
        # Get recent activities
        team_activities = Activity.query.filter(
            Activity.team_id == current_team.id
        ).order_by(Activity.created_at.desc()).limit(10).all()
        
        # Get team members
        team_members = db.session.query(User, TeamMember.role).join(
            TeamMember, User.id == TeamMember.user_id
        ).filter(TeamMember.team_id == current_team.id).all()
    
    return render_template('dashboard.html',
                         user_teams=user_teams,
                         current_team=current_team,
                         recent_files=recent_files,
                         team_messages=team_messages,
                         team_activities=team_activities,
                         team_members=team_members)

@app.route('/switch_team/<int:team_id>')
@require_login
def switch_team(team_id):
    # Check if user is member of this team
    membership = TeamMember.query.filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if membership:
        session['current_team_id'] = team_id
        flash('Team switched successfully!', 'success')
    else:
        flash('You are not a member of this team.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/create_team', methods=['GET', 'POST'])
@require_login
def create_team():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Team name is required.', 'error')
            return render_template('team_create.html')
        
        # Generate unique invite code
        invite_code = secrets.token_urlsafe(12)
        
        # Create team
        team = Team(
            name=name,
            description=description,
            invite_code=invite_code,
            created_by=current_user.id
        )
        db.session.add(team)
        db.session.flush()  # Get team ID
        
        # Add creator as admin
        membership = TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role='admin'
        )
        db.session.add(membership)
        
        # Create default folder structure
        default_folder = Folder(
            name='General',
            team_id=team.id,
            created_by=current_user.id
        )
        db.session.add(default_folder)
        
        db.session.commit()
        
        # Log activity
        log_activity(team.id, 'create_team', 'team', team.id, f'Created team "{name}"')
        
        session['current_team_id'] = team.id
        flash('Team created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('team_create.html')

@app.route('/join_team', methods=['GET', 'POST'])
@require_login
def join_team():
    if request.method == 'POST':
        invite_code = request.form.get('invite_code', '').strip()
        
        if not invite_code:
            flash('Invite code is required.', 'error')
            return render_template('team_join.html')
        
        # Find team by invite code
        team = Team.query.filter_by(invite_code=invite_code).first()
        if not team:
            flash('Invalid invite code.', 'error')
            return render_template('team_join.html')
        
        # Check if already a member
        existing_membership = TeamMember.query.filter(
            TeamMember.team_id == team.id,
            TeamMember.user_id == current_user.id
        ).first()
        
        if existing_membership:
            flash('You are already a member of this team.', 'warning')
            session['current_team_id'] = team.id
            return redirect(url_for('dashboard'))
        
        # Add user to team
        membership = TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role='viewer'
        )
        db.session.add(membership)
        db.session.commit()
        
        # Log activity
        log_activity(team.id, 'join_team', 'team', team.id, f'{current_user.display_name} joined the team')
        
        session['current_team_id'] = team.id
        flash(f'Successfully joined team "{team.name}"!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('team_join.html')

@app.route('/files')
@require_login
def files():
    current_team_id = session.get('current_team_id')
    if not current_team_id:
        flash('Please select a team first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == current_team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        flash('You are not a member of this team.', 'error')
        return redirect(url_for('dashboard'))
    
    folder_id = request.args.get('folder', type=int)
    search_query = request.args.get('search', '').strip()
    
    # Get current folder
    current_folder = None
    if folder_id:
        current_folder = Folder.query.filter(
            Folder.id == folder_id,
            Folder.team_id == current_team_id
        ).first()
        if not current_folder:
            flash('Folder not found.', 'error')
            return redirect(url_for('files'))
    
    # Get folders in current directory
    folders = Folder.query.filter(
        Folder.team_id == current_team_id,
        Folder.parent_id == folder_id
    ).order_by(Folder.name).all()
    
    # Get files in current directory
    files_query = File.query.filter(
        File.team_id == current_team_id,
        File.folder_id == folder_id,
        File.is_deleted == False
    )
    
    # Apply search filter
    if search_query:
        files_query = files_query.filter(
            or_(
                File.original_filename.contains(search_query),
                File.file_type.contains(search_query)
            )
        )
    
    files = files_query.order_by(File.updated_at.desc()).all()
    
    # Get breadcrumb path
    breadcrumbs = []
    if current_folder:
        folder = current_folder
        while folder:
            breadcrumbs.insert(0, folder)
            folder = folder.parent
    
    return render_template('file_view.html',
                         folders=folders,
                         files=files,
                         current_folder=current_folder,
                         breadcrumbs=breadcrumbs,
                         search_query=search_query,
                         membership=membership)

@app.route('/upload', methods=['GET', 'POST'])
@require_login
def upload_file():
    current_team_id = session.get('current_team_id')
    if not current_team_id:
        flash('Please select a team first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check team membership and permissions
    membership = TeamMember.query.filter(
        TeamMember.team_id == current_team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role == 'viewer':
        flash('You do not have permission to upload files.', 'error')
        return redirect(url_for('files'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        folder_id = request.form.get('folder_id', type=int)
        
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Secure filename
            original_filename = file.filename
            filename = secure_filename(original_filename)
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            unique_filename = f"{file_id}.{file_extension}" if file_extension else file_id
            
            # Create team directory if it doesn't exist
            team_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_team_id))
            os.makedirs(team_upload_dir, exist_ok=True)
            
            file_path = os.path.join(team_upload_dir, unique_filename)
            
            try:
                file.save(file_path)
                file_size = os.path.getsize(file_path)
                file_type = get_file_type(original_filename)
                
                # Create file record
                new_file = File(
                    filename=unique_filename,
                    original_filename=original_filename,
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_type,
                    mime_type=file.content_type or 'application/octet-stream',
                    team_id=current_team_id,
                    folder_id=folder_id,
                    uploaded_by=current_user.id
                )
                db.session.add(new_file)
                db.session.flush()  # Get file ID
                
                # For text files, create initial version
                if file_type == 'text':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        version = FileVersion(
                            file_id=new_file.id,
                            version_number=1,
                            content=content,
                            created_by=current_user.id
                        )
                        db.session.add(version)
                    except Exception as e:
                        print(f"Error reading text file: {e}")
                
                db.session.commit()
                
                # Log activity
                log_activity(current_team_id, 'upload_file', 'file', new_file.id, 
                           f'Uploaded "{original_filename}"')
                
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('files', folder=folder_id))
                
            except Exception as e:
                print(f"Error uploading file: {e}")
                flash('Error uploading file.', 'error')
                return redirect(request.url)
        else:
            flash('File type not allowed. Please upload txt, md, docx, jpg, jpeg, png, gif, pdf, or svg files.', 'error')
            return redirect(request.url)
    
    # Get folders for upload form
    folder_id = request.args.get('folder', type=int)
    folders = Folder.query.filter(
        Folder.team_id == current_team_id
    ).order_by(Folder.name).all()
    
    return render_template('file_upload.html', folders=folders, current_folder_id=folder_id)

@app.route('/file/<int:file_id>')
@require_login
def view_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == file.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        flash('You do not have access to this file.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get file content for text files
    content = None
    if file.file_type == 'text':
        latest_version = FileVersion.query.filter(
            FileVersion.file_id == file.id
        ).order_by(FileVersion.version_number.desc()).first()
        
        if latest_version:
            content = latest_version.content
        else:
            try:
                with open(file.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                content = "Error reading file content."
    
    return render_template('file_view.html', file=file, content=content, membership=membership)

@app.route('/file/<int:file_id>/edit', methods=['GET', 'POST'])
@require_login
def edit_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check team membership and permissions
    membership = TeamMember.query.filter(
        TeamMember.team_id == file.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role == 'viewer':
        flash('You do not have permission to edit this file.', 'error')
        return redirect(url_for('view_file', file_id=file_id))
    
    if file.file_type != 'text':
        flash('Only text files can be edited.', 'error')
        return redirect(url_for('view_file', file_id=file_id))
    
    # Get current content
    latest_version = FileVersion.query.filter(
        FileVersion.file_id == file.id
    ).order_by(FileVersion.version_number.desc()).first()
    
    current_content = ""
    if latest_version:
        current_content = latest_version.content or ""
    else:
        try:
            with open(file.file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            current_content = ""
    
    if request.method == 'POST':
        new_content = request.form.get('content', '')
        
        try:
            # Save to file
            with open(file.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Create new version
            next_version = (latest_version.version_number + 1) if latest_version else 1
            version = FileVersion(
                file_id=file.id,
                version_number=next_version,
                content=new_content,
                created_by=current_user.id
            )
            db.session.add(version)
            
            # Update file metadata
            file.version = next_version
            file.updated_at = datetime.now()
            
            db.session.commit()
            
            # Log activity
            log_activity(file.team_id, 'edit_file', 'file', file.id, 
                        f'Edited "{file.original_filename}"')
            
            flash('File saved successfully!', 'success')
            return redirect(url_for('view_file', file_id=file_id))
            
        except Exception as e:
            print(f"Error saving file: {e}")
            flash('Error saving file.', 'error')
    
    # Get file versions for history
    versions = FileVersion.query.filter(
        FileVersion.file_id == file.id
    ).order_by(FileVersion.version_number.desc()).all()
    
    return render_template('file_edit.html', file=file, content=current_content, 
                         versions=versions, membership=membership)

@app.route('/download/<int:file_id>')
@require_login
def download_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == file.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        abort(403)
    
    try:
        return send_file(file.file_path, as_attachment=True, 
                        download_name=file.original_filename)
    except Exception as e:
        print(f"Error downloading file: {e}")
        flash('Error downloading file.', 'error')
        return redirect(url_for('view_file', file_id=file_id))

@app.route('/chat')
@require_login
def chat():
    current_team_id = session.get('current_team_id')
    if not current_team_id:
        flash('Please select a team first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == current_team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        flash('You are not a member of this team.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get team and messages
    team = Team.query.get(current_team_id)
    messages = Message.query.filter(
        Message.team_id == current_team_id
    ).order_by(Message.created_at.asc()).all()
    
    # Get team members
    team_members = db.session.query(User, TeamMember.role).join(
        TeamMember, User.id == TeamMember.user_id
    ).filter(TeamMember.team_id == current_team_id).all()
    
    return render_template('chat.html', team=team, messages=messages, 
                         team_members=team_members, membership=membership)

@app.route('/send_message', methods=['POST'])
@require_login
def send_message():
    current_team_id = session.get('current_team_id')
    if not current_team_id:
        flash('Please select a team first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == current_team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        flash('You are not a member of this team.', 'error')
        return redirect(url_for('dashboard'))
    
    content = request.form.get('content', '').strip()
    if not content:
        flash('Message cannot be empty.', 'error')
        return redirect(url_for('chat'))
    
    # Create message
    message = Message(
        content=content,
        team_id=current_team_id,
        sender_id=current_user.id
    )
    db.session.add(message)
    db.session.commit()
    
    # Log activity
    log_activity(current_team_id, 'send_message', 'message', message.id, 
                'Sent a message')
    
    return redirect(url_for('chat'))

@app.route('/settings', methods=['GET', 'POST'])
@require_login
def settings():
    if request.method == 'POST':
        theme = request.form.get('theme')
        if theme in ['light', 'dark']:
            current_user.theme_preference = theme
            db.session.commit()
            flash('Settings updated successfully!', 'success')
        else:
            flash('Invalid theme selection.', 'error')
    
    return render_template('settings.html')

@app.route('/create_folder', methods=['POST'])
@require_login
def create_folder():
    current_team_id = session.get('current_team_id')
    if not current_team_id:
        flash('Please select a team first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check permissions
    membership = TeamMember.query.filter(
        TeamMember.team_id == current_team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role == 'viewer':
        flash('You do not have permission to create folders.', 'error')
        return redirect(url_for('files'))
    
    folder_name = request.form.get('name', '').strip()
    parent_id = request.form.get('parent_id', type=int)
    
    if not folder_name:
        flash('Folder name is required.', 'error')
        return redirect(url_for('files', folder=parent_id))
    
    # Create folder
    folder = Folder(
        name=folder_name,
        team_id=current_team_id,
        parent_id=parent_id,
        created_by=current_user.id
    )
    db.session.add(folder)
    db.session.commit()
    
    # Log activity
    log_activity(current_team_id, 'create_folder', 'folder', folder.id, 
                f'Created folder "{folder_name}"')
    
    flash('Folder created successfully!', 'success')
    return redirect(url_for('files', folder=parent_id))

@app.route('/delete_file/<int:file_id>', methods=['POST'])
@require_login
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # Check permissions
    membership = TeamMember.query.filter(
        TeamMember.team_id == file.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership or (membership.role == 'viewer' and file.uploaded_by != current_user.id):
        flash('You do not have permission to delete this file.', 'error')
        return redirect(url_for('view_file', file_id=file_id))
    
    # Soft delete
    file.is_deleted = True
    file.deleted_at = datetime.now()
    db.session.commit()
    
    # Log activity
    log_activity(file.team_id, 'delete_file', 'file', file.id, 
                f'Deleted "{file.original_filename}"')
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('files', folder=file.folder_id))
