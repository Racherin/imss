import pytz
from . import db
import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin) :
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100))
    middle_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    dept_id = db.Column(db.Integer)  # Dept table eklenecek
    nationality = db.Column(db.String(200))
    address = db.Column(db.String(2000))
    phone = db.Column(db.String(100))
    last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Istanbul')))
    specialization = db.Column(db.String(200))
    waiting_student_requests = db.Column(db.String(3000))  # "['232323','3434343','323232']"
    avaliable_hours = db.Column(db.String(1000))  # "{'monday':'14.00-15.00','tuesday':....}"
    thesis_topic = db.Column(db.String(2000))
    # thesis_file = db.Column(db.Boolean, default=False)
    advisor_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)
    type_user = db.Column(db.String(200))

#
# class Advisor(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     first_name = db.Column(db.String(100))
#     middle_name = db.Column(db.String(100))
#     last_name = db.Column(db.String(100))
#     dept_id = db.Column(db.Integer)  # Dept table eklenecek
#     nationality = db.Column(db.String(200))
#     address = db.Column(db.String(2000))
#     phone = db.Column(db.String(100))
#     last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Istanbul')))
#     specialization = db.Column(db.String(200))
#     waiting_student_requests = db.Column(db.String(3000))  # "['232323','3434343','323232']"
#     avaliable_hours = db.Column(db.String(1000))  # "{'monday':'14.00-15.00','tuesday':....}"
#
#
# class Student(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(100), nullable=False)
#     first_name = db.Column(db.String(100))
#     middle_name = db.Column(db.String(100))
#     last_name = db.Column(db.String(100))
#     dept_id = db.Column(db.Integer)  # Dept table eklenecek
#     nationality = db.Column(db.String(200))
#     address = db.Column(db.String(2000))
#     phone = db.Column(db.String(100))
#     last_login = db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Istanbul')))
#     thesis_topic = db.Column(db.String(2000))
#     # thesis_file = db.Column(db.Boolean, default=False)
#     advisor_id = db.Column(db.Integer)
#     task_id = db.Column(db.Integer)


class Task(UserMixin, db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    task_desc = db.Column(db.String(1000))
    task_duedate = db.Column(db.DateTime)
    task_queue_no = db.Column(db.Integer)


class Department(UserMixin, db.Model):
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(1000))


class Proposal(UserMixin,db.Model) :
    proposal_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    student_id = db.Column(db.Integer)
    advisor_id = db.Column(db.Integer)
    thesis_topic = db.Column(db.String(400))
    is_accepted = db.Column(db.Boolean)
    sent_date =  db.Column(db.DateTime, default=datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Istanbul')))

