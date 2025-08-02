# 🚀 File Drive - Modern File Management Platform

A complete file management and collaboration platform built with Flask, featuring user authentication, team-based file sharing, and real-time chat functionality.

## ✨ Features

- 🔐 **User Authentication** - Secure signup, login, and session management
- 👥 **Team Management** - Create teams, invite members, manage roles
- 📁 **File Sharing** - Upload, download, and organize files with local storage
- 💬 **Real-time Chat** - Team communication with instant messaging
- 🎨 **Modern UI** - Responsive design with Bootstrap and custom styling
- 🔒 **Local Storage** - No external dependencies required for local use
- ☁️ **Optional S3** - AWS S3 integration for cloud storage (optional)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/filedrive.git
   cd filedrive
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Access the website**
   - Open your browser and go to: http://127.0.0.1:5000
   - Create an account and start using File Drive!

## 📁 Project Structure

```
filedrive/
├── main.py              # Application entry point
├── app.py               # Flask app configuration
├── routes.py            # All web routes and functionality
├── models.py            # Database models
├── auth.py              # Authentication system
├── s3_storage.py        # File storage (local/S3)
├── templates/           # HTML templates
├── static/              # CSS, JS, and static assets
├── uploads/             # Local file storage directory
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Configuration

- **Database**: SQLite (filedrive.db) - auto-created
- **File Storage**: Local uploads folder
- **Session**: Local development secret key
- **Port**: 5000 (configurable)

## 🎯 Usage

### For Users
1. **Sign Up** - Create a new account
2. **Create Team** - Start a team for collaboration
3. **Upload Files** - Share documents, images, and more
4. **Chat** - Communicate with team members
5. **Manage Files** - Organize and download shared files

### For Developers
- **Local Development** - No AWS credentials required
- **Extensible** - Easy to add new features
- **Well-documented** - Clear code structure and comments

## 🛠️ Development

### Running in Development Mode
```bash
python main.py
```

### Using the Windows Batch File
```bash
start_file_drive.bat
```

### Database Management
The SQLite database is automatically created when you first run the application.

## 🌐 Deployment

### Local Deployment
The application is ready to run locally without any external dependencies.

### Cloud Deployment
For production deployment:
1. Set up a production WSGI server (Gunicorn, uWSGI)
2. Configure environment variables
3. Set up a production database (PostgreSQL recommended)
4. Optionally configure AWS S3 for file storage

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🎉 Project Status

✅ **Fully Functional** - All features working  
✅ **Self-Contained** - No external dependencies  
✅ **Well-Documented** - Complete setup instructions  
✅ **Ready for Use** - Production-ready code  

---

**Built with ❤️ using Flask, SQLAlchemy, and Bootstrap**

**Project**: File Drive  
**Status**: ✅ Working  
**Last Updated**: August 2, 2025 