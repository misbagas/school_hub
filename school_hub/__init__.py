from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from flask_wtf.csrf import CSRFProtect
from requests import request, session

# Initialize db object
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'c0af5ac84d3fe3a898fbc6866c65d6bba8690a7891213e25')  # Using default fallback
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Root1234!@localhost/school_hub'
    app.config['SQLALCHEMY_BINDS'] = {
        'main': 'mysql://root:Root1234!@localhost/main_db',
        'teacher_db': 'mysql://root:Root1234!@localhost/teacher_db',
        'student_db': 'mysql://root:Root1234!@localhost/student_db',
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    csrf = CSRFProtect(app)
    
    # Initialize the app with the configurations
    db.init_app(app)
    migrate = Migrate(app, db)

    # Initialize LoginManager
    login_manager.init_app(app)
    
    # Define the user_loader function
    from school_hub.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Assumes user_id is an integer
    
    # Register Blueprint
    from school_hub.routes import main  # Import the Blueprint
    app.register_blueprint(main)  # Register the main Blueprint

    return app

# Initialize the app instance using the app factory pattern
app = create_app()
@app.before_request
def csrf_protect():
    if request.method == "POST" or request.method == "DELETE":
        csrf_token = request.headers.get('X-CSRFToken')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            return jsonify({'message': 'Invalid CSRF token'}), 403
# This should be done outside of the `create_app` function to avoid issues
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
