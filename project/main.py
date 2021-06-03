from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_login import login_required, current_user
from models import User, Proposal, Uploads, Prerequisite
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash
from obs import OBSWrapper
import re
main = Blueprint('main', __name__)

"""
This file includes some examples of how to handle HTTP requests about user pages and post requests from different users.
We pass the value '/' to @app.route() to signify that this function will respond to web requests for the URL /, which is
the login URL.
If @main.route() includes a methods=['POST'], that means we'll handle a post requests and redirect user to another page 
instead of rendering a html.
"""



@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.type_user == "student":
        obs_data = OBSWrapper(current_user.email)
        gpa = obs_data.get_user_gpa()
        course_list = obs_data.get_user_courses()
        courses = []
        for course in course_list:
            courses.append("" + course['name'] + " - " + course['lecturer'])
        department_advisor = obs_data.get_user_department_advisor()
        department_advisor_mail = obs_data.get_user_department_advisor_mail()
        department = obs_data.get_user_department()
        general_data = OBSWrapper("general")
        semester = general_data.get_semester()

        get_student = User.query.filter(User.id == current_user.id).first()
        thesis_advisor_name = ""
        if get_student.advisor_id is None:
            thesis_advisor_name = "You did not propose with any advisor yet."
        else:
            get_advisor_name = User.query.filter(User.id == get_student.advisor_id).first()
            thesis_advisor_name = get_advisor_name.first_name + " " + get_advisor_name.last_name

        get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                                   Proposal.is_accepted == "0")).all()
        proposal_count = len(get_proposals)
        data = {
            'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
            'usertype': str(current_user.type_user).title(),
            'proposal_count': proposal_count,
            'gpa': gpa,
            'courses': courses,
            'department_advisor': department_advisor,
            'department_advisor_mail': department_advisor_mail,
            'department': department,
            'semester': semester,
            'thesis_advisor': thesis_advisor_name,
            'user_photo': OBSWrapper(current_user.email).get_photo(),

        }
        return render_template("dashboard.html", data=data)
    else:

        get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                                   Proposal.is_accepted == "0")).all()
        proposal_count = len(get_proposals)

        filelist = []
        forms = Uploads.query.order_by(Uploads.id.desc()).limit(5).all()

        for form in forms:
            get_student = User.query.filter(User.id == form.student_id).first()
            if get_student.advisor_id == current_user.id:
                filelist.append({'file_name': form.form_name, 'submission_date': form.submission_date,'student_name':get_student.first_name + " "+get_student.last_name,'student_id':get_student.id})


        obs_data = OBSWrapper("general")
        obs_data_advisor = OBSWrapper(current_user.email)

        get_student_list = len(User.query.filter(User.advisor_id == current_user.id).all())

        data = {
            'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
            'usertype': str(current_user.type_user).title(),
            'proposal_count': proposal_count,
            'user_photo': OBSWrapper(current_user.email).get_photo(),
            'formlist': filelist,
            'semester' : obs_data.get_semester(),
            'department' : obs_data_advisor.get_user_department(),
            'student_count' : get_student_list

        }
        return render_template("dashboardadvisor.html", data=data)


@main.route('/list-student')
@login_required
def list_students():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "1")).all()

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count,
        'user_photo': OBSWrapper(current_user.email).get_photo(),

    }
    return render_template("displaystudent.html", data=data)


@login_required
@main.route('/studentlist')
def students():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "1")).all()

    student_list = User.query.filter(User.advisor_id == current_user.id).all()

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count,
        'student_list': student_list,
        'user_photo': OBSWrapper(current_user.email).get_photo(),

    }
    return render_template("liststudents.html", data=data)


@login_required
@main.route('/student/<id>')
def display_student(id):
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "1")).all()

    get_student = User.query.filter(User.id == int(id)).first()

    student_obs = OBSWrapper(get_student.email)

    courses = student_obs.get_user_courses()


    gpa = student_obs.get_user_gpa()
    form_list = Uploads.query.filter(Uploads.student_id == get_student.id).all()
    photo = student_obs.get_photo()

    prerequisities = Prerequisite.query.filter().all()
    student_prereq = student_obs.get_user_prerequisites()

    print(student_prereq)
    prerequisite_list = []
    for prereq in prerequisities:
        prerequisite_list.append(
            {
                "name" : prereq.prerequisite_description,
                "status" : student_obs.get_user_prerequisites()[str(prereq.id)]
            }
        )


    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'user_photo': OBSWrapper(current_user.email).get_photo(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count,
        'student': get_student,
        'gpa': gpa,
        'courses': courses,
        'photo': photo,
        'forms': form_list,
        'prerequisites': prerequisite_list,

    }
    return render_template("displaystudent.html", data=data)



