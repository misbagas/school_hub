from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from school_hub.forms import EmployeeForm, LoginForm, RegisterForm
from .models import AssignmentReminder, ClassCode, StudentClassCode, User
from . import db

# Configure logging (ensure this is only done once, ideally in your main application file)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Blueprint definition
main = Blueprint('main', __name__)


# Home route
@main.route('/')
def index():
    return render_template('index.html')



# Login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_or_username = form.email_or_username.data
        password = form.password.data

        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        if user and check_password_hash(user.password_hash, password):  # Ensure password_hash is used
            login_user(user)
            print(f"User logged in: {user.username}, Role: {user.role}")  # Log the role on login
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html', form=form)

# Registration route
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # Create an instance of the form
    if form.validate_on_submit():  # Use validate_on_submit() for easier validation
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data

        # Check for existing user
        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash('Email or username already exists.', 'danger')
        else:
            # Hash the password without specifying the method (default is 'pbkdf2:sha256')
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password, role=role)  # Notice 'password_hash' here
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.login'))

    return render_template('register.html', form=form)  # Pass the form to the template
# Dashboard route
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return render_template('student_dashboard.html', user=current_user)
    elif current_user.role == 'teacher':
        return render_template('teacher_dashboard.html', user=current_user)
    elif current_user.role == 'employee':
        form = EmployeeForm()  # Create an instance of the form
        return render_template('employee_dashboard.html', user=current_user, form=form)
    elif current_user.role == 'parent':
        return render_template('parent_dashboard.html', user=current_user)
    else:
        flash('Unauthorized role!', 'danger')
        return redirect(url_for('main.index'))
    

@main.route('/save_class_code', methods=['POST'])
@login_required
def save_class_code():
    if current_user.role != 'employee':  # Role-based access
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    code = data.get('code', '').strip()
    description = data.get('description', '').strip()

    if not code or not description:
        return jsonify({'message': 'Both code and description are required.'}), 400

    existing_code = ClassCode.query.filter_by(code=code).first()
    if existing_code:
        return jsonify({'message': 'Class code already exists.'}), 400

    new_class_code = ClassCode(
        code=code,
        description=description,
        creator_id=current_user.id
    )
    db.session.add(new_class_code)
    db.session.commit()

    return jsonify({'id': new_class_code.id, 'message': 'Class code saved successfully!'}), 200


@main.route('/get_class_codes', methods=['GET'])
@login_required
def get_class_codes():
    print(f"User ID: {current_user.id}, Role: {current_user.role}")  # Add this for more clarity
    if current_user.role == 'teacher':
        class_codes = ClassCode.query.filter_by(creator_id=current_user.id).all()
    elif current_user.role == 'student':
        class_codes = (
            db.session.query(StudentClassCode, ClassCode)
            .join(ClassCode, StudentClassCode.class_code_id == ClassCode.id)
            .filter(StudentClassCode.student_id == current_user.id)
            .all()
        )
        class_codes = [c[1] for c in class_codes]
    else:
        return jsonify({'message': f'Unauthorized role: {current_user.role}'}), 403

    result = [{'code': c.code, 'description': c.description} for c in class_codes]
    return jsonify({'class_codes': result}), 200



@main.route('/join_class', methods=['POST'])
@login_required
def join_class():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    class_code = data.get('code', '').strip()

    if not class_code:
        return jsonify({'success': False, 'message': 'Class code cannot be empty!'}), 400

    class_code_entry = ClassCode.query.filter_by(code=class_code).first()

    if not class_code_entry:
        return jsonify({'success': False, 'message': 'Invalid class code!'}), 404

    existing_join = StudentClassCode.query.filter_by(
        student_id=current_user.id,
        class_code_id=class_code_entry.id
    ).first()

    if existing_join:
        return jsonify({'success': False, 'message': 'You have already joined this class.'}), 400

    student_class_code = StudentClassCode(
        code=class_code_entry.code,
        student_id=current_user.id,
        class_code_id=class_code_entry.id,
        joined_at=datetime.utcnow()
    )
    db.session.add(student_class_code)
    db.session.commit()

    return jsonify({'success': True, 'message': 'You have successfully joined the class!'}), 200


@main.route('/delete_class_code/<int:id>', methods=['DELETE'])
@login_required
def delete_class_code(id):
    if current_user.role != 'employee':
        return jsonify({'message': 'Unauthorized'}), 403

    class_code = ClassCode.query.get(id)
    if not class_code:
        return jsonify({'message': 'Class code not found.'}), 404

    db.session.delete(class_code)
    db.session.commit()

    return jsonify({'message': 'Class code deleted successfully!'}), 200

@main.route('/class/<string:class_code>', methods=['GET'])
@login_required
def class_page(class_code):
    class_code_entry = ClassCode.query.filter_by(code=class_code).first()

    if not class_code_entry:
        flash('Class not found!', 'danger')
        return redirect(url_for('main.dashboard'))

    # Fetch additional details if needed
    return render_template('class_page.html', class_code=class_code_entry)

@main.route('/create_assignment', methods=['POST'])
@login_required
def create_assignment():
    if current_user.role != 'teacher':  # Restrict to teachers
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    due_date = data.get('due_date', '').strip()

    if not title or not description or not due_date:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    try:
        due_date = datetime.strptime(due_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid due date format.'}), 400

    new_assignment = AssignmentReminder(
        title=title,
        description=description,
        due_date=due_date,
        user_id=current_user.id
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Assignment created successfully!'}), 200


# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

# Additional routes (e.g., contact, about, etc.)
@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')
