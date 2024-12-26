# database.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):  # Custom base class for SQLAlchemy
    pass

db = SQLAlchemy(model_class=Base)
migrate = Migrate()

def get_db():
    return db
