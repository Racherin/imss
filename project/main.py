from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_login import login_required, current_user
from models import User, Proposal
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash


main = Blueprint('main', __name__)


"""
This file includes some examples of how to handle HTTP requests about user pages and post requests from different users.
We pass the value '/' to @app.route() to signify that this function will respond to web requests for the URL /, which is
the login URL.
If @main.route() includes a methods=['POST'], that means we'll handle a post requests and redirect user to another page 
instead of rendering a html.
"""


@main.route('/')
def index():
    return render_template("login2.html")


@main.route('/dashboard')
@login_required
def dashboard():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'proposal_count':proposal_count
    }
    return render_template("dashboard.html", data=data)


@main.route('/propose-advisor')
@login_required
def propose_advisor():

    all_advisors = User.query.filter(User.type_user == 'advisor').all()
    get_student = User.query.filter(User.id == current_user.id).first()
    print(get_student.advisor_id,"asdadasdasda")
    if get_student.advisor_id is not None :
        get_accepted_advisor = User.query.filter(User.id == get_student.advisor_id).first()
        flash("Your proposal is already accepted by "+ get_accepted_advisor.first_name+" "+get_accepted_advisor.last_name,"success")
        return redirect(url_for('main.dashboard'))

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_advisors': all_advisors,

    }
    return render_template("proposeadvisor.html", data=data)


@main.route('/createproposal', methods=['POST'])
def acceptpropsal():
    advisorid = request.form.get('advisorid')
    studentid = current_user.id
    email = current_user.email
    student_name = str(current_user.first_name + " " + current_user.last_name)
    thesis_topic = request.form.get('thesistopic')
    new_proposal = Proposal(student_id=studentid, advisor_id=advisorid, thesis_topic=thesis_topic,
                            student_name=student_name,student_mail=email)
    db.session.add(new_proposal)
    db.session.commit()
    flash("You have successfully proposed to advisor.","success")
    return redirect(url_for('main.dashboard'))


@main.route('/my-proposals')
@login_required
def my_proposals():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count

    }
    return render_template("acceptreject.html", data=data)


@main.route('/proposal-answer-accept', methods=['POST'])
def answer_proposal_accept():
    std_id = request.form.get('student_id')
    prop_id = request.form.get('proposal_id')
    my_proposal = Proposal.query.filter(Proposal.proposal_id == prop_id).first()
    my_proposal.is_accepted = "1"
    my_student = User.query.filter(User.id == std_id).first()
    my_student.advisor_id = current_user.id
    flash("You have successfully accepted student's proposal.","success")
    db.session.commit()
    return redirect(url_for('main.my_proposals'))


@main.route('/proposal-answer-reject', methods=['POST'])
def answer_proposal_reject():
    prop_id = request.form.get('proposal_id')
    print(prop_id)
    my_proposal = Proposal.query.filter(Proposal.proposal_id == prop_id).first()
    my_proposal.is_accepted = "2"
    flash("You have successfully rejected student's proposal.","danger")
    db.session.commit()
    return redirect(url_for('main.my_proposals'))




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
        'proposal_count': proposal_count

    }
    return render_template("liststudents.html", data=data)

@main.route('/updatepassword')
def update_password():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "1")).all()
    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count

    }

    return render_template("updatepassword.html",data=data)

@main.route("/updatepassword",methods=['POST'])
def update_password_post():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    new_password_again = request.form.get("new_password2")

    if not new_password == new_password_again :
        flash("Passwords are not match.","danger")
        return redirect(url_for("main.update_password"))

    user = User.query.filter_by(
        email=current_user.email).first()

    if not check_password_hash(user.password, current_password) :
        flash("Please enter correct password","danger")
        return redirect(url_for("main.update_password"))

    user.password = generate_password_hash(new_password)

    db.session.commit()

    flash("Password change successfull","success")
    return redirect(url_for("main.update_password"))
