from wtforms import DateField, StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email
from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired
import os

class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateTimeField('Due Date', format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    submit = SubmitField('Create Reminder')
    class_code = StringField('Class Code', validators=[DataRequired()])

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'misbahskuy')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '2431307')
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Register as', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('employee', 'Employee')
    ], validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email_or_username = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('student', 'Student'), ('teacher', 'Teacher'), ('parent', 'Parent'), ('employee', 'Employee')], validators=[DataRequired()])
    submit = SubmitField('Login')

# Define a simple form (or use any form you need)
class TeacherDashboardForm(FlaskForm):
    some_field = StringField('Some Field', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EmployeeForm(FlaskForm):
    code = StringField(
        'Class Code',
        validators=[DataRequired(), Length(max=20, message="Code must be 20 characters or less.")],
    )
    description = StringField(
        'Description',
        validators=[DataRequired(), Length(max=255, message="Description must be 255 characters or less.")],
    )
    submit = SubmitField('Generate Code')

class GenerateClassCodeForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Generate Code')

class ClassCodeForm(FlaskForm):
    class_code = StringField('Class Code', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])  # Add a title field if needed
    submit = SubmitField('Submit Class Code')
    description = TextAreaField('Description', validators=[DataRequired()])
    due_date = DateField('Due Date', validators=[DataRequired()])

class JoinClassForm(FlaskForm):
    submit = SubmitField('Join Class')

class StudentForm(FlaskForm):
    # Define the fields you need
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Submit')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')