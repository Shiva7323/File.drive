# File Drive - Setup Guide

## ✅ Current Status: WORKING

The application is now running successfully on:
- **Local**: http://127.0.0.1:5000
- **Network**: http://192.168.1.76:5000

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python main.py
   ```

3. **Access the Application**:
   - Open your browser to http://127.0.0.1:5000
   - Use the demo mode or create an account

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file in the project root for production:

```env
# Database (PostgreSQL for production)
DATABASE_URL=postgresql://username:password@localhost:5432/filedrive

# Session Security
SESSION_SECRET=your-super-secret-session-key-here

# Replit OAuth (if using Replit)
REPL_ID=your-replit-id-here

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET_NAME=your-s3-bucket-name
```

### Default Configuration

If no `.env` file is present, the app uses these defaults:
- **Database**: SQLite (`filedrive.db`)
- **Session Secret**: Development key (change for production)
- **Storage**: Local file system
- **Authentication**: Email-based login

## 🛠️ Architecture

### Backend
- **Framework**: Flask 3.1.1
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **Authentication**: Email + Replit OAuth
- **File Storage**: Local + AWS S3 (optional)

### Frontend
- **Templates**: Jinja2 with Bootstrap 5
- **Styling**: Glassmorphism design
- **JavaScript**: Vanilla JS with Bootstrap components

## 📁 Project Structure

```
MongoFastTracker/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── config.py           # Configuration management
├── database.py         # Database initialization
├── models.py           # SQLAlchemy models
├── routes.py           # Flask routes
├── replit_auth.py     # OAuth authentication
├── s3_storage.py      # AWS S3 integration
├── templates/          # HTML templates
├── static/            # CSS, JS, images
├── uploads/           # File storage
└── pyproject.toml     # Dependencies
```

## 🔍 Features

### ✅ Working Features
- User authentication (email + OAuth)
- Team creation and management
- File upload and management
- Real-time chat system
- File versioning
- Role-based permissions
- Dark/light theme toggle
- Mobile-responsive design

### 🔧 Recent Fixes
- Fixed circular import issues
- Added graceful AWS S3 fallback
- Improved error handling
- Added development defaults
- Fixed database configuration

## 🚨 Troubleshooting

### Common Issues

1. **Port 5000 in use**:
   ```bash
   # Change port in main.py
   app.run(host="0.0.0.0", port=5001, debug=True)
   ```

2. **Database errors**:
   ```bash
   # Delete and recreate database
   rm filedrive.db
   python main.py
   ```

3. **Permission errors**:
   ```bash
   # Ensure uploads directory exists
   mkdir uploads
   ```

## 🎯 Next Steps

1. **Production Deployment**:
   - Set up PostgreSQL database
   - Configure proper session secrets
   - Set up AWS S3 for file storage
   - Use Gunicorn for production server

2. **Additional Features**:
   - Email verification
   - Two-factor authentication
   - Advanced file sharing
   - Real-time notifications

## 📞 Support

The application is now fully functional and ready for development and testing! 