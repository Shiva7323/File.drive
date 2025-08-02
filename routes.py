import os
import secrets
import uuid
from datetime import datetime
from urllib.parse import urlparse
from werkzeug.utils import secure_filename
from flask import session, render_template, request, redirect, url_for, flash, send_file, jsonify, abort
from flask_login import login_user, logout_user
from flask_login import current_user
from sqlalchemy import or_
from s3_storage import upload_to_s3, delete_from_s3, get_download_url, s3_storage

from app import app, db
from auth import require_login
from models import User, Team, TeamMember, File, Folder, Message, Activity, FileVersion, UploadPermission



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

def can_upload_file(team_id, user_id):
    """Check if user can upload files to the team"""
    # Allow everyone to upload files - no restrictions
    return True

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/mobile')
def mobile_home():
    """Mobile-optimized home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('mobile_index.html')

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

# Authentication Routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate username
        is_valid_username, username_error = User.validate_username(username)
        if not is_valid_username:
            flash(username_error, 'error')
            return render_template('signup.html')
        
        # Validate password
        is_valid_password, password_error = User.validate_password(password)
        if not is_valid_password:
            flash(password_error, 'error')
            return render_template('signup.html')
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken. Please choose a different username.', 'error')
            return render_template('signup.html')
        
        # Create new user with only username and password
        user = User.create_user(username, password, None, '', '')
        db.session.add(user)
        db.session.commit()
        
        # Store verification word in session for display
        session['verification_word'] = user.verification_word
        
        # Log in the user
        login_user(user)
        flash('Account created successfully! Welcome to File Drive.', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('login.html')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_url = session.get('next_url')
            if next_url:
                session.pop('next_url', None)
                return redirect(next_url)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        verification_word = request.form.get('verification_word')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not verification_word or not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('forgot_password.html')
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('forgot_password.html')
        
        # Validate password strength
        is_valid, error_msg = User.validate_password(new_password)
        if not is_valid:
            flash(error_msg, 'error')
            return render_template('forgot_password.html')
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('Username not found', 'error')
            return render_template('forgot_password.html')
        
        # Verify the verification word
        if user.verification_word.lower() != verification_word.lower():
            flash('Invalid verification word', 'error')
            return render_template('forgot_password.html')
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        flash('Password updated successfully! You can now sign in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/switch_mode/<mode>')
@require_login
def switch_mode(mode):
    """Switch between single and team modes"""
    if mode not in ['single', 'team']:
        flash('Invalid mode selected', 'error')
        return redirect(url_for('dashboard'))
    
    current_user.mode_preference = mode
    db.session.commit()
    
    flash(f'Switched to {mode} mode', 'success')
    return redirect(url_for('dashboard'))

# Enhanced File Editor Routes
@app.route('/edit/<int:file_id>')
@require_login
def edit_file(file_id):
    """Enhanced file editor with syntax highlighting and real-time features"""
    file = File.query.get_or_404(file_id)
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == file.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        flash('You do not have access to this file.', 'error')
        return redirect(url_for('files'))
    
    if membership and membership.role == 'viewer':
        flash('You do not have permission to edit this file.', 'error')
        return redirect(url_for('files'))
    
    # Check if file is text-editable
    if file.file_type not in ['text', 'document'] or file.original_filename.split('.')[-1].lower() not in ['txt', 'md', 'py', 'js', 'html', 'css', 'json', 'xml']:
        flash('This file type cannot be edited online.', 'error')
        return redirect(url_for('files'))
    
    # Get file content
    file_content = ''
    try:
        if file.storage_type == 's3' and file.s3_key:
            # Get content from S3
            if s3_storage.is_configured():
                # For now, we'll ask user to download and re-upload for S3 files
                flash('S3 files cannot be edited directly yet. Please download and re-upload.', 'info')
                return redirect(url_for('files'))
        else:
            # Get content from local file
            with open(file.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
    except Exception as e:
        flash(f'Error reading file: {str(e)}', 'error')
        return redirect(url_for('files'))
    
    return render_template('editor.html', file=file, file_content=file_content)

@app.route('/edit/<int:file_id>', methods=['POST'])
@require_login
def save_file_edit(file_id):
    """Save edited file content"""
    file = File.query.get_or_404(file_id)
    
    # Check permissions
    membership = TeamMember.query.filter(
        TeamMember.team_id == file.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership or (membership and membership.role == 'viewer'):
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    content = request.form.get('content', '')
    
    try:
        if file.storage_type == 'local':
            # Save to local file
            with open(file.file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update file metadata
            file.updated_at = datetime.now()
            file.version += 1
            
            # Create file version record
            version = FileVersion(
                file_id=file.id,
                version_number=file.version,
                content=content,
                created_by=current_user.id
            )
            db.session.add(version)
            db.session.commit()
            
            # Log activity
            log_activity(
                file.team_id, 
                current_user.id, 
                'file_edit', 
                'file', 
                file.id, 
                f"Updated {file.original_filename}"
            )
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'S3 files cannot be edited yet'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/dashboard')
@require_login
def dashboard():
    # Check user's mode preference
    user_mode = getattr(current_user, 'mode_preference', 'team')
    
    if user_mode == 'single':
        # Single mode - show only user's personal files
        recent_files = File.query.filter(
            File.uploaded_by == current_user.id,
            File.is_deleted == False,
            File.team_id.is_(None)  # Personal files have no team
        ).order_by(File.updated_at.desc()).limit(10).all()
        
        # In single mode, we don't show team data
        user_teams = []
        current_team = None
        team_messages = []
        team_activities = []
        team_members = []
        
    else:
        # Team mode - show team data
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
                         team_members=team_members,
                         user_mode=user_mode)

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
        
        # Add user to team as editor by default (so they can upload files)
        membership = TeamMember(
            team_id=team.id,
            user_id=current_user.id,
            role='editor'
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
    user_mode = getattr(current_user, 'mode_preference', 'team')
    
    if user_mode == 'single':
        # Single mode - show personal files
        current_team_id = None
        membership = None
    else:
        # Team mode - check team requirements
        current_team_id = session.get('current_team_id')
        if not current_team_id:
            flash('Please select a team first.', 'warning')
            return redirect(url_for('dashboard'))
        
        # No membership restrictions - everyone can access all teams
        membership = TeamMember.query.filter(
            TeamMember.team_id == current_team_id,
            TeamMember.user_id == current_user.id
        ).first()
    
    folder_id = request.args.get('folder', type=int)
    search_query = request.args.get('search', '').strip()
    
    # Get current folder
    current_folder = None
    if folder_id:
        if user_mode == 'single':
            # In single mode, folders are not supported yet
            flash('Folders are not supported in single mode.', 'warning')
            return redirect(url_for('files'))
        else:
            current_folder = Folder.query.filter(
                Folder.id == folder_id,
                Folder.team_id == current_team_id
            ).first()
            if not current_folder:
                flash('Folder not found.', 'error')
                return redirect(url_for('files'))
    
    # Get folders in current directory
    if user_mode == 'single':
        folders = []  # No folders in single mode
    else:
        folders = Folder.query.filter(
            Folder.team_id == current_team_id,
            Folder.parent_id == folder_id
        ).order_by(Folder.name).all()
    
    # Get files in current directory
    if user_mode == 'single':
        files_query = File.query.filter(
            File.team_id.is_(None),  # Personal files
            File.uploaded_by == current_user.id,
            File.folder_id == folder_id,
            File.is_deleted == False
        )
    else:
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
                         membership=membership,
                         user_mode=user_mode)

@app.route('/upload', methods=['GET', 'POST'])
@require_login
def upload_file():
    user_mode = getattr(current_user, 'mode_preference', 'team')
    
    if user_mode == 'single':
        # Single mode - upload to personal space
        current_team_id = None
        can_upload = True  # Users can always upload in single mode
        team = None
        membership = None
    else:
        # Team mode - check team permissions
        current_team_id = session.get('current_team_id')
        if not current_team_id:
            flash('Please select a team first.', 'warning')
            return redirect(url_for('dashboard'))
        
        # No membership restrictions - everyone can upload to any team
        membership = TeamMember.query.filter(
            TeamMember.team_id == current_team_id,
            TeamMember.user_id == current_user.id
        ).first()
        
        team = Team.query.get(current_team_id)
    
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
            
            # Check for duplicate file in the same location
            if user_mode == 'single':
                existing_file = File.query.filter(
                    File.team_id.is_(None),  # Personal files
                    File.uploaded_by == current_user.id,
                    File.folder_id == folder_id,
                    File.original_filename == original_filename,
                    File.is_deleted == False
                ).first()
            else:
                existing_file = File.query.filter(
                    File.team_id == current_team_id,
                    File.folder_id == folder_id,
                    File.original_filename == original_filename,
                    File.is_deleted == False
                ).first()
            
            if existing_file:
                flash(f'A file with the name "{original_filename}" already exists in this location.', 'error')
                return redirect(request.url)
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            unique_filename = f"{file_id}.{file_extension}" if file_extension else file_id
            
            file_type = get_file_type(original_filename)
            storage_type = 'local'
            s3_key = None
            file_path = None
            
            try:
                # Try S3 upload first if configured
                if s3_storage.is_configured():
                    file.seek(0)  # Reset file pointer
                    s3_key, file_url = upload_to_s3(file, current_team_id, original_filename)
                    if s3_key:
                        storage_type = 's3'
                        file_path = file_url
                        file.seek(0, 2)  # Seek to end for size
                        file_size = file.tell()
                    else:
                        # S3 failed, fall back to local
                        file.seek(0)
                        
                # Local storage fallback or primary
                if not s3_key:
                    if user_mode == 'single':
                        # Create personal directory
                        personal_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'personal', str(current_user.id))
                        os.makedirs(personal_upload_dir, exist_ok=True)
                        file_path = os.path.join(personal_upload_dir, unique_filename)
                    else:
                        # Create team directory
                        team_upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(current_team_id))
                        os.makedirs(team_upload_dir, exist_ok=True)
                        file_path = os.path.join(team_upload_dir, unique_filename)
                    
                    file.save(file_path)
                    file_size = os.path.getsize(file_path)
                
                # Create file record
                new_file = File(
                    filename=unique_filename,
                    original_filename=original_filename,
                    file_path=file_path,
                    file_size=file_size,
                    file_type=file_type,
                    mime_type=file.content_type or 'application/octet-stream',
                    storage_type=storage_type,
                    s3_key=s3_key,
                    team_id=current_team_id,  # None for single mode
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
                
                # Log activity (only in team mode)
                if user_mode == 'team' and current_team_id:
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
    if user_mode == 'single':
        folders = []  # No folders in single mode for now
    else:
        folders = Folder.query.filter(
            Folder.team_id == current_team_id
        ).order_by(Folder.name).all()
    
    return render_template('file_upload.html', folders=folders, current_folder_id=folder_id, user_mode=user_mode)

@app.route('/file/<int:file_id>')
@require_login
def view_file(file_id):
    file = File.query.get_or_404(file_id)
    
    # No access restrictions - everyone can view all files
    user_mode = current_user.mode_preference
    
    if user_mode == 'single':
        membership = None # No team membership in single mode
    else:
        # In team mode, get membership for UI purposes only
        if file.team_id:
            membership = TeamMember.query.filter(
                TeamMember.team_id == file.team_id,
                TeamMember.user_id == current_user.id
            ).first()
        else:
            membership = None
    
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
def edit_file_simple(file_id):
    file = File.query.get_or_404(file_id)
    
    # No access restrictions - everyone can edit all files
    user_mode = current_user.mode_preference
    
    if user_mode == 'single':
        membership = None # No team membership in single mode
    else:
        # In team mode, get membership for UI purposes only
        if file.team_id:
            membership = TeamMember.query.filter(
                TeamMember.team_id == file.team_id,
                TeamMember.user_id == current_user.id
            ).first()
        else:
            membership = None
    
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
            
            # Log activity (only for team mode)
            if file.team_id:
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
    
    # No access restrictions - everyone can download all files
    user_mode = current_user.mode_preference
    
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

@app.route('/delete_message/<int:message_id>', methods=['POST'])
@require_login
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Check if user can delete this message
    # Users can delete their own messages, admins can delete any message
    membership = TeamMember.query.filter(
        TeamMember.team_id == message.team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        return jsonify({'success': False, 'error': 'Access denied'})
    
    can_delete = (message.sender_id == current_user.id or (membership and membership.role == 'admin'))
    if not can_delete:
        return jsonify({'success': False, 'error': 'Permission denied'})
    
    # Soft delete the message
    message.is_deleted = True
    message.deleted_at = datetime.now()
    db.session.commit()
    
    # Log activity
    log_activity(message.team_id, 'delete_message', 'message', message.id, 
                f'Deleted a message')
    
    return jsonify({'success': True})

@app.route('/edit_message/<int:message_id>', methods=['POST'])
@require_login
def edit_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Only sender can edit their own messages within 5 minutes
    if message.sender_id != current_user.id:
        return jsonify({'success': False, 'error': 'Only message sender can edit'})
    
    # Check if message is still editable (within 5 minutes)
    time_diff = datetime.now() - message.created_at
    if time_diff.total_seconds() > 300:  # 5 minutes
        return jsonify({'success': False, 'error': 'Message can only be edited within 5 minutes'})
    
    new_content = request.form.get('content', '').strip()
    if not new_content:
        return jsonify({'success': False, 'error': 'Message cannot be empty'})
    
    message.content = new_content
    message.is_edited = True
    message.edited_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'content': new_content})

@app.route('/team/<int:team_id>/settings', methods=['GET', 'POST'])
@require_login
def team_settings(team_id):
    team = Team.query.get_or_404(team_id)
    
    # Check team membership
    membership = TeamMember.query.filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership:
        flash('You are not a member of this team.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST' and membership and membership.role == 'admin':
        # Update team settings
        team.name = request.form.get('team_name', team.name)
        team.description = request.form.get('team_description', team.description)
        
        # Update upload permission mode
        upload_mode = request.form.get('upload_permission_mode', 'role_based')
        if upload_mode in ['role_based', 'selected_users', 'everyone']:
            team.upload_permission_mode = upload_mode
        
        # Update role-based permissions
        team.allow_editor_uploads = 'allow_editor_uploads' in request.form
        team.allow_viewer_uploads = 'allow_viewer_uploads' in request.form
        
        # Handle selected users permissions
        if upload_mode == 'selected_users':
            # Clear existing permissions
            UploadPermission.query.filter_by(team_id=team_id).delete()
            
            # Add new permissions
            selected_users = request.form.getlist('selected_users')
            for user_id in selected_users:
                if user_id != current_user.id:  # Don't add duplicate for admin
                    permission = UploadPermission(
                        team_id=team_id,
                        user_id=user_id,
                        granted_by=current_user.id
                    )
                    db.session.add(permission)
        
        db.session.commit()
        flash('Team settings updated successfully!', 'success')
        return redirect(url_for('team_settings', team_id=team_id))
    
    # Get team statistics
    team_members = db.session.query(User, TeamMember.role).join(
        TeamMember, User.id == TeamMember.user_id
    ).filter(TeamMember.team_id == team_id).all()
    
    team_files_count = File.query.filter(
        File.team_id == team_id,
        File.is_deleted == False
    ).count()
    
    team_messages_count = Message.query.filter(
        Message.team_id == team_id,
        Message.is_deleted == False
    ).count()
    
    # Get upload permissions for selected users mode
    upload_permissions = []
    if team.upload_permission_mode == 'selected_users':
        upload_permissions = UploadPermission.query.filter_by(team_id=team_id).all()
    
    return render_template('team_settings.html',
                         team=team,
                         membership=membership,
                         team_members=team_members,
                         team_files_count=team_files_count,
                         team_messages_count=team_messages_count,
                         upload_permissions=upload_permissions)

@app.route('/team/<int:team_id>/change_role/<string:user_id>', methods=['POST'])
@require_login
def change_member_role(team_id, user_id):
    """Change a team member's role (admin only)"""
    # Check if current user is admin of this team
    membership = TeamMember.query.filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()
    
    if not membership or membership.role != 'admin':
        flash('Only team administrators can change member roles.', 'error')
        return redirect(url_for('team_settings', team_id=team_id))
    
    # Get the member to change
    target_membership = TeamMember.query.filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id
    ).first()
    
    if not target_membership:
        flash('Member not found.', 'error')
        return redirect(url_for('team_settings', team_id=team_id))
    
    # Get new role from form
    new_role = request.form.get('role')
    if new_role not in ['admin', 'editor', 'viewer']:
        flash('Invalid role.', 'error')
        return redirect(url_for('team_settings', team_id=team_id))
    
    # Don't allow changing the team creator's role
    team = Team.query.get(team_id)
    if user_id == team.created_by and new_role != 'admin':
        flash('Cannot change the team creator\'s role.', 'error')
        return redirect(url_for('team_settings', team_id=team_id))
    
    # Update role
    old_role = target_membership.role
    target_membership.role = new_role
    db.session.commit()
    
    # Log activity
    user = User.query.get(user_id)
    log_activity(team_id, 'change_role', 'member', target_membership.id, 
                f'Changed {user.display_name} role from {old_role} to {new_role}')
    
    flash(f'Successfully changed {user.display_name}\'s role to {new_role}.', 'success')
    return redirect(url_for('team_settings', team_id=team_id))

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
    
    # No restrictions - everyone can create folders
    
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
    
    # No access restrictions - everyone can delete all files
    user_mode = current_user.mode_preference
    
    # Soft delete
    file.is_deleted = True
    file.deleted_at = datetime.now()
    db.session.commit()
    
    # Log activity (only for team mode)
    if file.team_id:
        log_activity(file.team_id, 'delete_file', 'file', file.id, 
                    f'Deleted "{file.original_filename}"')
    
    flash('File deleted successfully!', 'success')
    return redirect(url_for('files', folder=file.folder_id))

@app.route('/help')
def help_page():
    """Help and guidelines page"""
    return render_template('help.html')

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback submission page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not name or not subject or not message:
            flash('Please fill in all required fields.', 'error')
            return render_template('feedback.html')
        
        # In a real application, you would save this to database or send email
        # For now, we'll just show a success message
        flash('Thank you for your feedback! We will get back to you soon.', 'success')
        return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

@app.route('/about')
def about():
    """About page with application information"""
    return render_template('about.html')
