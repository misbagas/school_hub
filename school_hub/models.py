from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from school_hub import db
from sqlalchemy.orm import relationship

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
    assignments = db.relationship('AssignmentReminder', foreign_keys='AssignmentReminder.user_id', back_populates='creator')  # This line is fine
    class_codes = db.relationship('ClassCode', back_populates='creator')
    created_users = db.relationship('User', backref=db.backref('creator_user', remote_side=[id]), lazy=True)

    creator = db.relationship('User', remote_side=[id], backref=db.backref('created_by_user', lazy='dynamic'))

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



class AssignmentReminder(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relationships
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    creator = db.relationship('User', foreign_keys=[user_id], back_populates='assignments')

    def __repr__(self):
        return f"<AssignmentReminder(title={self.title})>"


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return f"<Announcement(title={self.title})>"

class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships
    users = db.relationship('User', back_populates='class_info')
    students = db.relationship('Student', back_populates='class_info')

    def __repr__(self):
        return f"<Class(name={self.name})>"

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

    # Relationships
    class_info = db.relationship('Class', back_populates='students')

    def __repr__(self):
        return f"<Student(first_name={self.first_name}, last_name={self.last_name})>"

class Teacher(db.Model):
    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relationships
    assignments = db.relationship('Assignment', back_populates='teacher', lazy=True)

    def __repr__(self):
        return f"<Teacher(name={self.name})>"

class Assignment(db.Model):
    __tablename__ = 'assignments'
    __table_args__ = {'extend_existing': True}  # Allow redefining the table

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    class_code_id = db.Column(db.Integer, db.ForeignKey('class_code.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    teacher = db.relationship('Teacher', back_populates='assignments')
    class_code = db.relationship('ClassCode', backref=db.backref('assignments', lazy=True))

    def __repr__(self):
        return f"<Assignment(title={self.title})>"

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
