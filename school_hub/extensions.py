from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()  # This is the shared instance of SQLAlchemy
login_manager = LoginManager()
