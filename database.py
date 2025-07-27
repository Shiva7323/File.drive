from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Create a single db instance that can be imported by both app.py and models.py
db = SQLAlchemy(model_class=Base) 