from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from school_hub.forms import EmployeeForm, LoginForm, RegisterForm, MessageForm
from .models import ClassCode, StudentClassCode, User, ClassJoin, Message, Assignment, AssignmentReminder
from . import db
import os
from werkzeug.utils import secure_filename

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Blueprint definition
main = Blueprint('main', __name__)

# Helper function to check file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------- Authentication Routes --------------------
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_or_username = form.email_or_username.data
        password = form.password.data

        user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        role = form.role.data

        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash('Email or username already exists.', 'danger')
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# -------------------- Dashboard Routes --------------------
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return render_template('student_dashboard.html', user=current_user)
    elif current_user.role == 'teacher':
        return render_template('teacher_dashboard.html', user=current_user)
    elif current_user.role == 'employee':
        form = EmployeeForm()
        class_codes = ClassCode.query.filter_by(creator_id=current_user.id).all()
        return render_template('employee_dashboard.html', user=current_user, form=form, class_codes=class_codes)
    elif current_user.role == 'parent':
        return render_template('parent_dashboard.html', user=current_user)
    flash('Unauthorized role!', 'danger')
    return redirect(url_for('main.index'))


# -------------------- Class Code Routes --------------------
@main.route('/save_class_code', methods=['POST'])
@login_required
def save_class_code():
    data = request.get_json()
    code = data.get('code')
    description = data.get('description')

    if not code or not description:
        return jsonify({'message': 'Code and description are required'}), 400

    new_class_code = ClassCode(code=code, description=description, creator_id=current_user.id)
    try:
        db.session.add(new_class_code)
        db.session.commit()
        return jsonify({'message': 'Class code saved successfully', 'id': new_class_code.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error saving class code: {str(e)}'}), 500

@main.route('/get_class_codes', methods=['GET'])
@login_required
def get_class_codes():
    if current_user.role not in ['teacher', 'employee']:  # Allow both teachers and employees
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    # Fetch all class codes (not filtered by creator_id)
    class_codes = ClassCode.query.all()
    return jsonify([{'code': code.code, 'description': code.description} for code in class_codes])

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


# -------------------- Student Routes --------------------
@main.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.index'))

    assignments = AssignmentReminder.query.filter_by(recipient_id=current_user.id).order_by(AssignmentReminder.due_date).all()

    # Fetch joined class codes
    joined_classes = (
        db.session.query(ClassCode.code, ClassCode.description)
        .join(StudentClassCode, StudentClassCode.class_code_id == ClassCode.id)
        .filter(StudentClassCode.student_id == current_user.id)
        .all()
    )

    return render_template('student_dashboard.html', assignments=assignments, joined_classes=joined_classes)

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

    existing_join = StudentClassCode.query.filter_by(student_id=current_user.id, class_code_id=class_code_entry.id).first()
    if existing_join:
        return jsonify({'success': False, 'message': 'You have already joined this class.'}), 400

    # Explicitly add code and description
    student_class_code = StudentClassCode(
        code=class_code_entry.code,  # Ensure this field is populated
        description=class_code_entry.description,  # Ensure description is provided
        student_id=current_user.id,
        class_code_id=class_code_entry.id,
        joined_at=datetime.utcnow()
    )

    db.session.add(student_class_code)
    db.session.commit()
    return jsonify({'success': True, 'message': 'You have successfully joined the class!'}), 200

@main.route('/get_joined_classes', methods=['GET'])
@login_required
def get_joined_classes():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    joined_classes = (
        db.session.query(ClassCode.code, ClassCode.description)
        .join(StudentClassCode, ClassCode.id == StudentClassCode.class_code_id)
        .filter(StudentClassCode.student_id == current_user.id)
        .all()
    )

    class_list = [{'code': c[0], 'description': c[1]} for c in joined_classes]

    return jsonify({'success': True, 'class_codes': class_list})

# -------------------- Teacher Routes --------------------
@main.route('/create_assignment', methods=['POST'])
@login_required
def create_assignment():
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    due_date = data.get('due_date', '').strip()
    class_code = data.get('class_code', '').strip()

    # Validate inputs
    if not title or not description or not due_date or not class_code:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    try:
        due_date_obj = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid due date format.'}), 400

    # Verify the class code exists
    class_code_entry = ClassCode.query.filter_by(code=class_code).first()
    if not class_code_entry:
        return jsonify({'success': False, 'message': 'Invalid class code.'}), 404

    # Create the Assignment (REMOVED student_id)
    new_assignment = Assignment(
        name=title,
        description=description,
        due_date=due_date_obj,
        teacher_id=current_user.id,
        class_id=class_code_entry.id
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Assignment created successfully!'}), 200


@main.route('/get_joined_students', methods=['GET'])
@login_required
def get_joined_students():
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    class_code = request.args.get('class_code')
    if not class_code:
        return jsonify({'success': False, 'message': 'Class code is required'}), 400

    # Verify the class code exists
    class_code_entry = ClassCode.query.filter_by(code=class_code).first()
    if not class_code_entry:
        return jsonify({'success': False, 'message': 'Class code not found'}), 404

    # Fetch students enrolled in the class
    joined_students = StudentClassCode.query.filter_by(class_code_id=class_code_entry.id).all()
    students_data = [{
        'id': student.student_id,
        'username': student.student.username,
        'email': student.student.email
    } for student in joined_students]

    return jsonify({'success': True, 'students': students_data, 'class_code': class_code_entry.code})

@main.route('/teacher_dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.index'))

    # Fetch all class sections taught by this teacher
    class_sections = Class.query.join(ClassJoin, Class.id == ClassJoin.class_id).filter(ClassJoin.teacher_id == current_user.id).all()

    # Fetch assignments created by this teacher
    assignments = (
        db.session.query(
            Assignment.id, 
            Assignment.name.label("title"),  # Fix column name
            Assignment.description, 
            Assignment.due_date,
            Class.name.label("class_name"),  # Correct join with Class, not ClassCode
            User.username.label("teacher_username")
        )
        .join(Class, Assignment.class_id == Class.id)  # Correct join
        .join(User, Assignment.teacher_id == User.id)
        .filter(Assignment.teacher_id == current_user.id)
        .order_by(Assignment.due_date)
        .all()
    )

    # Convert to list of dictionaries
    assignment_list = [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "due_date": a.due_date.strftime('%Y-%m-%d'),
            "class_name": a.class_name,  # Use class name instead of code
            "teacher_username": a.teacher_username
        }
        for a in assignments
    ]

    return render_template('teacher_dashboard.html', class_sections=class_sections, assignments=assignment_list)


@main.route('/get_teacher_assignments', methods=['GET'])
@login_required
def get_teacher_assignments():
    if current_user.role != 'teacher':
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    assignments = (
        db.session.query(
            Assignment.id, 
            Assignment.name, 
            Assignment.description, 
            Assignment.due_date,
            ClassCode.code.label("class_code"),
            User.username.label("teacher_username")
        )
        .join(ClassCode, Assignment.class_id == ClassCode.id)
        .join(User, Assignment.teacher_id == User.id)
        .filter(Assignment.teacher_id == current_user.id)
        .order_by(Assignment.due_date)
        .all()
    )

    assignment_list = [
        {
            "id": a.id,
            "name": a.name,
            "description": a.description,
            "due_date": a.due_date.strftime("%Y-%m-%d %H:%M"),
            "class_code": a.class_code,
            "teacher_username": a.teacher_username
        }
        for a in assignments
    ]

    return jsonify({"success": True, "assignments": assignment_list})



@main.route('/get_assignments', methods=['GET'])
@login_required
def get_assignments():
    if current_user.role != 'student':
        return jsonify({'success': False, 'message': 'Unauthorized access'}), 403

    # Fetch the student’s joined class IDs
    student_classes = StudentClassCode.query.filter_by(student_id=current_user.id).all()
    class_ids = [sc.class_code_id for sc in student_classes]

    print(f"Student {current_user.id} is in classes: {class_ids}")  # Debugging log

    # Fetch assignments from those classes
    assignments = Assignment.query.filter(Assignment.class_id.in_(class_ids)).all()
    
    if not assignments:
        print("No assignments found for this student.")  # Debugging log

    # Convert to JSON format
    assignment_list = [
        {
            'title': assignment.name,
            'description': assignment.description,
            'due_date': assignment.due_date.strftime('%Y-%m-%d')
        }
        for assignment in assignments
    ]

    print(f"Assignments sent to frontend: {assignment_list}")  # Debugging log
    return jsonify({'success': True, 'assignments': assignment_list})

# -------------------- Message Routes --------------------
@main.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    form = MessageForm()
    if form.validate_on_submit():
        content = form.content.data
        receiver_username = request.form.get("receiver")

        receiver = User.query.filter_by(username=receiver_username).first()
        if not receiver:
            flash("User not found!", "danger")
            return redirect(url_for("main.messages"))

        message = Message(sender_id=current_user.id, receiver_id=receiver.id, content=content, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        return redirect(url_for("main.messages"))

    messages = Message.query.filter((Message.sender_id == current_user.id) | (Message.receiver_id == current_user.id)).order_by(Message.timestamp.desc()).all()
    return render_template("messages.html", form=form, messages=messages)

@main.route('/delete_message/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    if message.sender_id != current_user.id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    db.session.delete(message)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message deleted successfully'})


# -------------------- Profile and File Upload Routes --------------------
@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST' and 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            current_user.profile_picture = filename
            db.session.commit()
            flash('Profile picture updated successfully!', 'success')
    return render_template('profile.html', user=current_user)

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# -------------------- Forum Routes --------------------
@main.route('/forum/<class_code>', methods=['GET', 'POST'])
@login_required
def forum(class_code):
    # Fetch the class code entry
    class_entry = ClassCode.query.filter_by(code=class_code).first()
    if not class_entry:
        flash('Class not found!', 'danger')
        return redirect(url_for('main.dashboard'))

    # Fetch all messages for this class forum
    messages = Message.query.filter(Message.class_code_id == class_code).order_by(Message.timestamp.asc()).all()

    # If the user submits a new message
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_message = Message(
                sender_id=current_user.id,
                content=content,
                class_code=class_code,
                timestamp=datetime.utcnow()
            )
            db.session.add(new_message)
            db.session.commit()
            flash('Message posted!', 'success')
            return redirect(url_for('main.forum', class_code=class_code))

    return render_template('forum.html', class_code=class_code, messages=messages)


# -------------------- Additional Routes --------------------
@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')