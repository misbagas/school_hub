from datetime import datetime
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from school_hub.forms import EmployeeForm, LoginForm, RegisterForm, MessageForm
from .models import ClassCode, StudentClassCode, User, ClassJoin, Message # Import ClassJoin
from . import db
import os
from werkzeug.utils import secure_filename

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

main = Blueprint('main', __name__)

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

@main.route('/search_contacts')
@login_required
def search_contacts():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    contacts = User.query.filter((User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))).limit(5).all()
    return jsonify([{ "id": user.id, "username": user.username, "email": user.email} for user in contacts])
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
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    user = current_user  # Retrieve the current logged-in user
    if current_user.role == 'student':
        return render_template('student_dashboard.html', user=current_user)
    elif current_user.role == 'teacher':
        return render_template('teacher_dashboard.html', user=current_user)
    elif current_user.role == 'employee':
        form = EmployeeForm()  # Create an instance of the form
        
        # Retrieve class codes created by the employee
        class_codes = ClassCode.query.filter_by(creator_id=current_user.id).all()
        
        return render_template('employee_dashboard.html', 
                               user=current_user, 
                               form=form,
                               class_codes=class_codes)  # Pass class codes to the template
    elif current_user.role == 'parent':
        return render_template('parent_dashboard.html', user=current_user)
    else:
        flash('Unauthorized role!', 'danger')
        return redirect(url_for('main.index'))



@main.route('/student_dashboard', methods=['GET'])
@login_required
def student_dashboard():
    if current_user.role == 'student':
        assignments = AssignmentReminder.query.order_by(AssignmentReminder.due_date).all()
        return render_template('student_dashboard.html', assignments=assignments)
    flash("Unauthorized access!", "danger")
    return redirect(url_for('main.index'))


@main.route('/save_class_code', methods=['POST'])
@login_required
def save_class_code():
    data = request.get_json()
    print(f"Received data: {data}")  # Debugging line

    code = data.get('code')
    description = data.get('description')

    if not code or not description:
        return jsonify({'message': 'Code and description are required'}), 400

    new_class_code = ClassCode(code=code, description=description, creator_id=current_user.id)
    try:
        db.session.add(new_class_code)
        db.session.commit()
        print(f"Class code saved: {new_class_code}")  # Debugging line
        return jsonify({'message': 'Class code saved successfully', 'id': new_class_code.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error saving class code: {e}")  # Debugging line
        return jsonify({'message': 'Error saving class code'}), 500


@main.route('/get_class_codes', methods=['GET'])
@login_required
def get_class_codes():
    try:
        # Fetch all class codes created by the current user
        class_codes = ClassCode.query.filter_by(creator_id=current_user.id).all()
        
        # Serialize the data into a JSON-friendly format
        class_codes_list = [
            {'id': code.id, 'code': code.code, 'description': code.description} 
            for code in class_codes
        ]
        return jsonify(class_codes_list), 200
    except Exception as e:
        logging.error(f"Error fetching class codes: {e}")
        return jsonify({'message': 'Error fetching class codes'}), 500


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
    recipient_id = data.get('recipient_id')

    if not title or not description or not due_date or not recipient_id:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400

    try:
        due_date = datetime.strptime(due_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid due date format.'}), 400

    recipient = User.query.get(recipient_id)
    if not recipient or recipient.role != 'student':
        return jsonify({'success': False, 'message': 'Invalid recipient.'}), 404

    new_assignment = AssignmentReminder(
        title=title,
        description=description,
        due_date=due_date,
        user_id=current_user.id,
        recipient_id=recipient_id
    )
    db.session.add(new_assignment)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Assignment created successfully!'}), 200
@main.route('/get_students', methods=['GET'])
@login_required
def get_students():
    if current_user.role != 'teacher':  # Restrict to teachers
        return jsonify({'message': 'Unauthorized'}), 403

    # Fetch students assigned to the teacher's class
    students = User.query.filter_by(role='student', class_id=current_user.class_id).all()

    return jsonify({
        'students': [{'id': s.id, 'username': s.username, 'email': s.email} for s in students]
    })


@main.route('/get_assignments', methods=['GET'])
@login_required
def get_assignments():
    assignments = AssignmentReminder.query.order_by(AssignmentReminder.due_date).all()
    return jsonify([{
        'title': a.title,
        'description': a.description,
        'due_date': a.due_date.strftime('%Y-%m-%d')
    } for a in assignments])


@main.route('/get_joined_students', methods=['GET'])
@login_required
def get_joined_students():
    if current_user.role != 'teacher':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    # Get class_code from the query string
    class_code = request.args.get('class_code')
    if not class_code:
        return jsonify({'success': False, 'message': 'Class code is required'}), 400

    # Fetch the class using the provided class code
    class_code_entry = ClassCode.query.filter_by(code=class_code).first()
    if not class_code_entry:
        return jsonify({'success': False, 'message': 'Class code not found'}), 404

    # Get all students who joined using this class code
    joined_students = StudentClassCode.query.filter_by(class_code_id=class_code_entry.id).all()
    students_data = []

    for join in joined_students:
        student = User.query.get(join.student_id)
        if student:
            students_data.append({
                'id': student.id,
                'username': student.username,
                'email': student.email
            })

    return jsonify({'success': True, 'students': students_data})


# In routes.py (or where the function is)
def get_joined_students():
    from school_hub.models import ClassJoin  # Import inside the function
    joined_students = ClassJoin.query.filter_by(teacher_id=current_user.id).all()
    return render_template('joined_students.html', students=joined_students)

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


@main.route('/search_contacts')
@login_required
def search_contacts():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    contacts = User.query.filter((User.username.ilike(f"%{query}%")) | (User.email.ilike(f"%{query}%"))).limit(5).all()
    return jsonify([{"id": user.id, "username": user.username, "email": user.email} for user in contacts])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main.route('/profile', methods=['GET', 'POST'])
def profile():
    user = User.query.get(current_user.id)  # Assuming you're using Flask-Login for current_user

    if request.method == 'POST':
        # Check if the profile picture is part of the request
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            
            # If the user uploads a file, save it
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)  # Ensure the filename is safe
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)  # Use current_app here
                file.save(file_path)

                # Update the user's profile picture in the database
                user.profile_picture = filename
                db.session.commit()

        return redirect(url_for('main.profile'))

    return render_template('profile.html', user=user)
    
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
