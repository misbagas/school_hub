from .models import User  # Import your User model

def get_user_role(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return user.role  # Assuming your User model has a role attribute
    return None
