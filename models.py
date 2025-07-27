from datetime import datetime
import uuid
import re
import random
import string
from app import db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    theme_preference = db.Column(db.String, default='light')  # light or dark
    mode_preference = db.Column(db.String, default='team')  # 'single' or 'team'
    verification_word = db.Column(db.String(20), nullable=False)  # For password recovery
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    team_memberships = db.relationship('TeamMember', back_populates='user', cascade='all, delete-orphan')
    uploaded_files = db.relationship('File', back_populates='uploader')
    messages = db.relationship('Message', back_populates='sender')

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password_hash(self.password_hash, password) if self.password_hash else False
    
    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        else:
            return f"User {self.id[:8]}"
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username:
            return False, "Username is required"
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        if len(username) > 50:
            return False, "Username must be less than 50 characters"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        return True, ""
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$', password):
            return False, "Password can only contain letters, numbers, and special characters"
        return True, ""
    
    @staticmethod
    def generate_verification_word():
        """Generate a random verification word between 6-20 characters"""
        # List of common words that are easy to remember
        words = [
            'apple', 'banana', 'cherry', 'dragon', 'eagle', 'forest', 'garden', 'harbor',
            'island', 'jungle', 'knight', 'lemon', 'mountain', 'ocean', 'palm', 'queen',
            'river', 'sunset', 'tiger', 'umbrella', 'village', 'window', 'yellow', 'zebra',
            'butterfly', 'chocolate', 'dolphin', 'elephant', 'fireworks', 'giraffe',
            'hamburger', 'icecream', 'jellyfish', 'kangaroo', 'lighthouse', 'moonlight',
            'notebook', 'octopus', 'penguin', 'rainbow', 'sunflower', 'turtle', 'volcano',
            'waterfall', 'xylophone', 'yacht', 'zucchini'
        ]
        return random.choice(words)
    
    @staticmethod
    def create_user(username, password, email=None, first_name=None, last_name=None):
        """Create a new user"""
        user = User()
        user.id = str(uuid.uuid4())
        user.username = username
        user.email = email if email and email.strip() else None  # Store None instead of empty string
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(password)
        user.verification_word = User.generate_verification_word()
        return user



class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    invite_code = db.Column(db.String(20), unique=True, nullable=False)
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Admin control settings for file uploads
    allow_editor_uploads = db.Column(db.Boolean, default=True)
    allow_viewer_uploads = db.Column(db.Boolean, default=False)
    upload_permission_mode = db.Column(db.String(20), default='role_based')  # 'role_based', 'selected_users', 'everyone'
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    members = db.relationship('TeamMember', back_populates='team', cascade='all, delete-orphan')
    files = db.relationship('File', back_populates='team', cascade='all, delete-orphan')
    folders = db.relationship('Folder', back_populates='team', cascade='all, delete-orphan')
    messages = db.relationship('Message', back_populates='team', cascade='all, delete-orphan')

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='viewer')  # admin, editor, viewer
    joined_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    team = db.relationship('Team', back_populates='members')
    user = db.relationship('User', back_populates='team_memberships')
    
    __table_args__ = (UniqueConstraint('team_id', 'user_id', name='uq_team_user'),)

class UploadPermission(db.Model):
    __tablename__ = 'upload_permissions'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    granted_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    team = db.relationship('Team', foreign_keys=[team_id])
    user = db.relationship('User', foreign_keys=[user_id])
    granter = db.relationship('User', foreign_keys=[granted_by])
    
    __table_args__ = (UniqueConstraint('team_id', 'user_id', name='uq_upload_permission'),)

class Folder(db.Model):
    __tablename__ = 'folders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    team = db.relationship('Team', back_populates='folders')
    creator = db.relationship('User', foreign_keys=[created_by])
    parent = db.relationship('Folder', remote_side=[id], backref='subfolders')
    files = db.relationship('File', back_populates='folder')

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)  # Local path or S3 key
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    storage_type = db.Column(db.String(20), default='local')  # 'local' or 's3'
    s3_key = db.Column(db.String(500), nullable=True)  # S3 object key
    
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    uploaded_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)
    version = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    team = db.relationship('Team', back_populates='files')
    folder = db.relationship('Folder', back_populates='files')
    uploader = db.relationship('User', back_populates='uploaded_files')
    versions = db.relationship('FileVersion', back_populates='file', cascade='all, delete-orphan')

class FileVersion(db.Model):
    __tablename__ = 'file_versions'
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('files.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)  # For text files
    file_path = db.Column(db.String(500))  # For binary files
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    file = db.relationship('File', back_populates='versions')
    creator = db.relationship('User', foreign_keys=[created_by])

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file
    
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    sender_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=True)
    
    # Edit and deletion tracking
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    team = db.relationship('Team', back_populates='messages')
    sender = db.relationship('User', back_populates='messages')
    reply_to = db.relationship('Message', remote_side=[id], backref='replies')

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # upload, edit, delete, join, etc.
    target_type = db.Column(db.String(20))  # file, folder, message, etc.
    target_id = db.Column(db.Integer)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    team = db.relationship('Team', foreign_keys=[team_id])
    user = db.relationship('User', foreign_keys=[user_id])
