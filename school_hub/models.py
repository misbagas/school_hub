from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from school_hub import db


# User Model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    is_admin_field = db.Column(db.Boolean, default=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    class_info = db.relationship('Class', back_populates='users')
    assignments = db.relationship('AssignmentReminder', back_populates='user', foreign_keys='AssignmentReminder.user_id')
    class_codes = db.relationship('ClassCode', back_populates='creator')
    class_joins = db.relationship('ClassJoin', foreign_keys='ClassJoin.student_id', back_populates='student')
    teacher_classes = db.relationship('ClassJoin', foreign_keys='ClassJoin.teacher_id', back_populates='teacher')
    profile_picture = db.Column(db.String(120), nullable=True)  # Store filename of profile picture
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)  # <-- date_joined field
    # Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, role={self.role})>"


# Class Model
class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Relationships
    users = db.relationship('User', back_populates='class_info')
    students = db.relationship('Student', back_populates='class_info')
    class_joins = db.relationship('ClassJoin', back_populates='class_info')

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Ensure this points to users.id
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)

    # Relationships
    teacher = db.relationship('User', backref='teacher_assignments')  # Fix: Change to User
    class_info = db.relationship('Class', backref='assignments')
    reminders = db.relationship('AssignmentReminder', backref='assignment', lazy=True, cascade='all, delete-orphan')



# AssignmentReminder Model
class AssignmentReminder(db.Model):
    __tablename__ = 'assignment_reminders'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    reminder_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='assignments', foreign_keys=[user_id])


class ClassJoin(db.Model):
    __tablename__ = 'class_join'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Fix: Use users.id

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id], back_populates='class_joins')
    class_info = db.relationship('Class', back_populates='class_joins')
    teacher = db.relationship('User', foreign_keys=[teacher_id], back_populates='teacher_classes')

# # Teacher Model
# class Teacher(db.Model):
#     __tablename__ = 'teachers'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)

#     # Relationships
#     assignments = db.relationship('Assignment', back_populates='teacher')

#     def __repr__(self):
#         return f"<Teacher(name={self.name})>"


# ClassCode Model
class ClassCode(db.Model):
    __tablename__ = 'class_code'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    creator = db.relationship('User', back_populates='class_codes')

    def __repr__(self):
        return f"<ClassCode(code={self.code})>"


# StudentClassCode Model
class StudentClassCode(db.Model):
    __tablename__ = 'student_class_codes'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_code_id = db.Column(db.Integer, db.ForeignKey('class_code.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User', foreign_keys=[student_id])
    class_code = db.relationship('ClassCode', backref=db.backref('student_entries', lazy=True))

    def __repr__(self):
        return f"<StudentClassCode(code={self.code})>"


# Course Model (Optional)
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250))

    # Relationships
    students = db.relationship('Student', back_populates='course')

    def __repr__(self):
        return f"<Course(name={self.name})>"

# Employee Model (Optional)
class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Employee(name={self.name})>"

# Student Model
class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    enrollment_date = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    password_hash = db.Column(db.String(128), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True)  # Added ForeignKey

    # Relationships
    class_info = db.relationship('Class', back_populates='students')
    course = db.relationship('Course', back_populates='students')  # Back-populates Course.students

    def __repr__(self):
        return f"<Student(first_name={self.first_name}, last_name={self.last_name})>"

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_code_id = db.Column(db.Integer, db.ForeignKey('class_code.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(255), nullable=True)  # Add this line to store the file URL

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    class_code = db.relationship('ClassCode', backref='messages')

class ForumMembership(db.Model):
    __tablename__ = 'forum_membership'
    id = db.Column(db.Integer, primary_key=True)
    class_code_id = db.Column(db.Integer, db.ForeignKey('class_code.id'))
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Make sure 'users.id' is correct
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    class_code = db.relationship('ClassCode', backref='memberships')
    student = db.relationship('User', backref='forum_memberships')