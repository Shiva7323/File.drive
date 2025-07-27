from flask import Flask, render_template
from database import db
from config import Config
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database with app
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    print("Database tables created")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return "Hello! The app is working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 