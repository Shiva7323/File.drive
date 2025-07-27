from flask import Flask
from database import db
from replit_auth import require_login
import routes

def register_routes(app: Flask):
    """Register all routes with the Flask app"""
    
    # Before request
    app.before_request(routes.make_session_permanent)
    
    # Registration and authentication routes
    app.add_url_rule('/register_otp', 'register_otp', routes.register_otp, methods=['GET', 'POST'])
    app.add_url_rule('/verify_otp/<user_id>', 'verify_otp', routes.verify_otp, methods=['GET', 'POST'])
    
    # Main routes
    app.add_url_rule('/', 'index', routes.index)
    app.add_url_rule('/demo', 'demo_dashboard', routes.demo_dashboard)
    app.add_url_rule('/signup', 'signup', routes.signup, methods=['GET', 'POST'])
    app.add_url_rule('/login', 'login', routes.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', routes.logout)
    
    # File management routes
    app.add_url_rule('/edit/<int:file_id>', 'edit_file', require_login(routes.edit_file))
    app.add_url_rule('/edit/<int:file_id>', 'save_file_edit', require_login(routes.save_file_edit), methods=['POST'])
    app.add_url_rule('/help', 'help_page', routes.help_page)
    app.add_url_rule('/feedback', 'feedback', routes.feedback, methods=['GET', 'POST'])
    
    # Dashboard and team routes
    app.add_url_rule('/dashboard', 'dashboard', require_login(routes.dashboard))
    app.add_url_rule('/switch_team/<int:team_id>', 'switch_team', require_login(routes.switch_team))
    app.add_url_rule('/files', 'files', require_login(routes.files))
    app.add_url_rule('/upload', 'upload_file', require_login(routes.upload_file), methods=['GET', 'POST'])
    app.add_url_rule('/file/<int:file_id>', 'view_file', require_login(routes.view_file))
    app.add_url_rule('/file/<int:file_id>/edit', 'edit_file_simple', require_login(routes.edit_file_simple), methods=['GET', 'POST'])
    app.add_url_rule('/download/<int:file_id>', 'download_file', require_login(routes.download_file))
    
    # Chat routes
    app.add_url_rule('/chat', 'chat', require_login(routes.chat))
    app.add_url_rule('/send_message', 'send_message', require_login(routes.send_message), methods=['POST'])
    app.add_url_rule('/delete_message/<int:message_id>', 'delete_message', require_login(routes.delete_message), methods=['POST'])
    app.add_url_rule('/edit_message/<int:message_id>', 'edit_message', require_login(routes.edit_message), methods=['POST'])
    
    # Team management routes
    app.add_url_rule('/team/<int:team_id>/settings', 'team_settings', require_login(routes.team_settings), methods=['GET', 'POST'])
    app.add_url_rule('/settings', 'settings', require_login(routes.settings), methods=['GET', 'POST'])
    app.add_url_rule('/create_folder', 'create_folder', require_login(routes.create_folder), methods=['POST'])
    app.add_url_rule('/delete_file/<int:file_id>', 'delete_file', require_login(routes.delete_file), methods=['POST'])
    
    # Team creation and management
    app.add_url_rule('/team/create', 'create_team', require_login(routes.create_team), methods=['GET', 'POST'])
    app.add_url_rule('/team/join', 'join_team', require_login(routes.join_team), methods=['GET', 'POST'])
    app.add_url_rule('/team/<int:team_id>/leave', 'leave_team', require_login(routes.leave_team), methods=['POST'])
    app.add_url_rule('/team/<int:team_id>/invite', 'invite_to_team', require_login(routes.invite_to_team), methods=['POST'])
    app.add_url_rule('/team/<int:team_id>/member/<user_id>/role', 'update_member_role', require_login(routes.update_member_role), methods=['POST'])
    app.add_url_rule('/team/<int:team_id>/member/<user_id>/remove', 'remove_team_member', require_login(routes.remove_team_member), methods=['POST'])
    app.add_url_rule('/team/<int:team_id>/transfer', 'transfer_team_ownership', require_login(routes.transfer_team_ownership), methods=['POST'])
    
    # Bin management routes
    app.add_url_rule('/clear_recent_files', 'clear_recent_files', require_login(routes.clear_recent_files), methods=['POST'])
    app.add_url_rule('/bin', 'bin', require_login(routes.bin))
    app.add_url_rule('/restore_file/<int:file_id>', 'restore_file', require_login(routes.restore_file), methods=['POST'])
    app.add_url_rule('/permanently_delete_file/<int:file_id>', 'permanently_delete_file', require_login(routes.permanently_delete_file), methods=['POST'])
    app.add_url_rule('/empty_bin', 'empty_bin', require_login(routes.empty_bin), methods=['POST'])
    
    # Team photo and single user mode
    app.add_url_rule('/team/<int:team_id>/upload_photo', 'upload_team_photo', require_login(routes.upload_team_photo), methods=['POST'])
    app.add_url_rule('/toggle_single_user_mode', 'toggle_single_user_mode', require_login(routes.toggle_single_user_mode), methods=['POST'])
    app.add_url_rule('/single_user_dashboard', 'single_user_dashboard', require_login(routes.single_user_dashboard))
    app.add_url_rule('/single_user_files', 'single_user_files', require_login(routes.single_user_files))
    app.add_url_rule('/single_user_upload', 'single_user_upload', require_login(routes.single_user_upload), methods=['GET', 'POST']) 