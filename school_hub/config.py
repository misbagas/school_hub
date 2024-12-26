import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '8d8a72493996de3050b75e0737fecacf'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
        'default': 'mysql+pymysql://root:Root1234!@localhost/school_hub',
        'main_db': 'mysql+pymysql://root:Root1234!@localhost/main_db',
        'teacher_db': 'mysql+pymysql://root:Root1234!@localhost/teacher_db',
        'student_db': 'mysql+pymysql://root:Root1234!@localhost/student_db'
    }
