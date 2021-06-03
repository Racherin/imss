import pytz
from app import db
import datetime
from flask_login import UserMixin

"""
We use models.py to create our database tables via SQLAlchemy classes. Columns provides define a table column.
Primary keys are marked with primary_key=True. 
"""


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    dept_id = db.Column(db.Integer)  # Dept table eklenecek
    nationality = db.Column(db.String(20))
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(
        pytz.timezone('Europe/Istanbul')))
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    type_user = db.Column(db.String(200))

    #Advisor
    specialization = db.Column(db.String(200))
    waiting_student_requests = db.Column(db.String(3000))  # "['232323','3434343','323232']"
    avaliable_hours = db.Column(db.String(1000))  # "{'monday':'14.00-15.00','tuesday':....}"

    #Student
    thesis_topic = db.Column(db.String(2000))
    thesis_file = db.Column(db.Boolean, default=False)
    advisor_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)



"""
class Student(User):
    __tablename__ = 'Student'
    
    id = db.Column(db.Integer, ForeignKey('User.id'), primary_key=True)
    thesis_topic = db.Column(db.String(2000))
    thesis_file = db.Column(db.Boolean, default=False)
    advisor_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)    
    
    __mapper_args__ = {
        'polymorphic_identity': 'Student',
    }


class Advisor(User):
    __tablename__ = 'Advisor'
    
    id = db.Column(db.Integer, ForeignKey('User.id'), primary_key=True)
    waiting_student_requests = db.Column(db.String(3000))  # "['232323','3434343','323232']"
    avaliable_hours = db.Column(db.String(1000))  # "{'monday':'14.00-15.00','tuesday':....}"
    
    __mapper_args__ = {
        'polymorphic_identity': 'Advisor',
    }
"""


class Task(UserMixin, db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_desc = db.Column(db.String(1000))
    task_duedate = db.Column(db.DateTime)
    task_queue_no = db.Column(db.Integer)


class Department(UserMixin, db.Model):
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(1000))


class Proposal(UserMixin, db.Model):
    proposal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(1000))
    student_id = db.Column(db.Integer)
    student_mail = db.Column(db.String(1000))
    advisor_id = db.Column(db.Integer)
    thesis_topic = db.Column(db.String(400))
    is_accepted = db.Column(db.String(10), default="0")  # 0 : proposalda, 1:accepted, 2:rejected
    sent_date = db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(
        pytz.timezone('Europe/Istanbul')))


class File(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_type = db.Column(db.String(1000))
    form_name = db.Column(db.String(1000))
    deadline = db.Column(db.DateTime)  # SORULACAK


class Uploads(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer)
    student_id = db.Column(db.Integer)
    is_checked = db.Column(db.Boolean, default=False)
    submission_date = db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(
        pytz.timezone('Europe/Istanbul')))
    file_path = db.Column(db.String(2000))
    file_name = db.Column(db.String(1000))
    form_name = db.Column(db.String(2000))


class Prerequisite(UserMixin, db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    prerequisite_description = db.Column(db.String(4000))
