# File Drive Project - Backup Instructions

## 🎯 Project Overview
**File Drive** - A modern file management and collaboration platform built with Flask.

## 📦 What's Included
- ✅ User authentication and registration
- ✅ Team-based file sharing
- ✅ Real-time chat functionality
- ✅ File upload/download with local storage
- ✅ Modern responsive UI with Bootstrap
- ✅ SQLite database for local development
- ✅ Optional AWS S3 integration (disabled for local use)

## 🚀 How to Run the Project

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation Steps
1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python main.py
   ```
4. **Access the website:**
   - Open browser and go to: http://127.0.0.1:5000
   - Create an account and start using File Drive!

## 📁 Important Files
- `main.py` - Application entry point
- `app.py` - Flask app configuration
- `routes.py` - All web routes and functionality
- `models.py` - Database models
- `auth.py` - Authentication system
- `s3_storage.py` - File storage (local/S3)
- `templates/` - HTML templates
- `static/` - CSS, JS, and static assets
- `uploads/` - Local file storage directory

## 🔧 Configuration
- **Database**: SQLite (filedrive.db) - auto-created
- **File Storage**: Local uploads folder
- **Session**: Local development secret key
- **Port**: 5000 (configurable)

## 💾 Backup Methods

### Method 1: Git Repository (Recommended)
```bash
git add .
git commit -m "Save project state"
git push origin main  # If you have a remote repository
```

### Method 2: ZIP Archive
1. Create a ZIP file of the entire project folder
2. Include all files except:
   - `__pycache__/` folders
   - `instance/` folder (database will be recreated)
   - `.git/` folder (if you want a clean backup)

### Method 3: Cloud Storage
- Upload the project folder to Google Drive, Dropbox, or OneDrive
- Consider using GitHub, GitLab, or Bitbucket for version control

## 🎉 Project Status: WORKING ✅
- ✅ Server running on http://127.0.0.1:5000
- ✅ User registration and login functional
- ✅ Team creation and management working
- ✅ File upload/download operational
- ✅ Local storage configured and working
- ✅ No AWS dependencies required for local use

## 📝 Notes
- The application uses local SQLite database
- Files are stored in the `uploads/` directory
- S3 storage is optional and disabled for local development
- All features are fully functional without external dependencies

---
**Last Updated**: August 2, 2025
**Status**: Fully Functional ✅ 