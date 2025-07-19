# File Drive - Team Collaboration Platform

## Overview

File Drive is a modern, secure, and collaborative file management platform built for teams and individuals. It provides real-time file sharing, integrated chat, and team management capabilities with a beautiful glassmorphism UI design.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: SQLAlchemy ORM with PostgreSQL (configurable via DATABASE_URL)
- **Authentication**: Replit OAuth integration with Flask-Login session management
- **File Storage**: Local filesystem with configurable upload directory
- **Session Management**: Flask sessions with proxy fix for HTTPS support

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5.1.3 with custom glassmorphism styles
- **Icons**: Font Awesome 6.0.0
- **JavaScript**: Vanilla JS with Bootstrap components
- **Theme Support**: Light/Dark mode toggle with CSS custom properties

### Database Schema
Key models include:
- **User**: Core user data with theme preferences and OAuth integration
- **Team**: Team management with invite codes and descriptions
- **TeamMember**: User-team relationships with role-based access (admin, editor, viewer)
- **File**: File metadata with versioning and type categorization
- **Folder**: Hierarchical file organization
- **Message**: Team chat functionality
- **Activity**: Team activity logging
- **OAuth**: Required for Replit authentication integration

## Key Components

### Authentication System
- **Primary Method**: Replit OAuth (mandatory tables: User, OAuth)
- **Session Storage**: Custom UserSessionStorage for OAuth tokens
- **Access Control**: Role-based permissions (admin, editor, viewer)
- **User Management**: Profile management with theme preferences

### File Management
- **Upload System**: Multi-file support with drag-and-drop interface
- **File Types**: Support for images, text files, documents (txt, md, docx, jpg, jpeg, png, gif, pdf, svg)
- **File Operations**: Upload, download, view, edit (for text files), delete
- **Version Control**: File versioning system
- **Organization**: Folder-based file hierarchy

### Team Collaboration
- **Team Creation**: Admin-controlled team setup with invite codes
- **Member Management**: Role-based access control
- **Real-time Chat**: Team messaging system
- **Activity Tracking**: Comprehensive activity logging
- **Team Switching**: Multi-team support per user

### User Interface
- **Design System**: Glassmorphism design with gradient backgrounds
- **Responsive Layout**: Mobile-first Bootstrap implementation
- **Theme System**: Light/dark mode with user preferences
- **Interactive Elements**: Smooth animations and transitions
- **Navigation**: Fixed navbar with contextual sidebar

## Data Flow

### File Upload Flow
1. User selects team and destination folder
2. File validation (type, size limits)
3. Secure filename processing
4. File storage in uploads directory
5. Database record creation with metadata
6. Activity logging for team visibility

### Authentication Flow
1. Replit OAuth initiation
2. Token storage in OAuth table
3. User session establishment
4. Team context loading
5. Permission-based UI rendering

### Chat System Flow
1. Message composition in team context
2. Real-time message storage
3. Team member notification
4. Activity stream updates

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **Flask-SQLAlchemy**: Database ORM
- **Flask-Login**: Session management
- **Flask-Dance**: OAuth integration
- **Werkzeug**: WSGI utilities and file handling
- **Pillow (PIL)**: Image processing
- **PyJWT**: Token handling

### Frontend Dependencies (CDN)
- **Bootstrap 5.1.3**: UI framework
- **Font Awesome 6.0.0**: Icon library

### Environment Variables
- **DATABASE_URL**: PostgreSQL connection string
- **SESSION_SECRET**: Flask session encryption key

## Deployment Strategy

### Development Setup
- **Host**: 0.0.0.0:5000
- **Debug Mode**: Enabled for development
- **Hot Reload**: Flask development server

### Production Considerations
- **Database**: PostgreSQL with connection pooling
- **File Storage**: Local filesystem (extensible to cloud storage)
- **Session Security**: Secure session key management
- **Proxy Support**: Configured for reverse proxy deployments
- **Upload Limits**: 16MB maximum file size
- **Database Optimization**: Pre-ping and connection recycling

### Security Features
- **CSRF Protection**: Flask session-based protection
- **File Validation**: Strict file type and size validation
- **Access Control**: Role-based permissions throughout
- **Secure Uploads**: Filename sanitization and validation
- **OAuth Integration**: Replit-managed authentication

The application follows a traditional MVC pattern with Flask, providing a solid foundation for team collaboration while maintaining security and scalability considerations.