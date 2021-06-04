from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from flask_login import login_required, current_user
from models import User, Proposal
from sqlalchemy import and_
from obs import OBSWrapper
from webmail import send_mail


proposal = Blueprint('proposal', __name__)


@proposal.route('/propose-advisor')
@login_required
def propose_advisor():
    all_advisors = User.query.filter(User.type_user == 'advisor').all()
    get_student = User.query.filter(User.id == current_user.id).first()
    if get_student.advisor_id is not None:
        get_accepted_advisor = User.query.filter(User.id == get_student.advisor_id).first()
        flash(
            "Your proposal is already accepted by " + get_accepted_advisor.first_name + " " + get_accepted_advisor.last_name,
            "success")
        return redirect(url_for('main.dashboard'))

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_advisors': all_advisors,
        'user_photo': OBSWrapper(current_user.email).get_photo(),

    }
    return render_template("proposeadvisor.html", data=data)


@proposal.route('/createproposal', methods=['POST'])
def createproposal():
    advisorid = request.form.get('advisorid')
    studentid = current_user.id
    email = current_user.email
    student_name = str(current_user.first_name + " " + current_user.last_name)
    thesis_topic = request.form.get('thesistopic')
    new_proposal = Proposal(student_id=studentid, advisor_id=advisorid, thesis_topic=thesis_topic,
                            student_name=student_name, student_mail=email)
    db.session.add(new_proposal)
    db.session.commit()
    flash("You have successfully proposed to advisor.", "success")
    return redirect(url_for('main.dashboard'))


@proposal.route('/my-proposals')
@login_required
def my_proposals():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count,
        'user_photo': OBSWrapper(current_user.email).get_photo(),

    }
    return render_template("acceptreject.html", data=data)


@proposal.route('/proposal-answer-accept', methods=['POST'])
def answer_proposal_accept():
    std_id = request.form.get('student_id')
    prop_id = request.form.get('proposal_id')
    my_proposal = Proposal.query.filter(Proposal.proposal_id == prop_id).first()
    my_proposal.is_accepted = "1"
    my_student = User.query.filter(User.id == std_id).first()
    my_student.advisor_id = current_user.id
    flash("You have successfully accepted student's proposal.", "success")
    db.session.commit()

    get_student = User.query.filter(User.id == my_proposal.student_id).first()

    get_advisor = User.query.filter(User.id == my_proposal.advisor_id).first()

    message = "Your proposal accepted by " + get_advisor.first_name+ " "+get_advisor.last_name

    send_mail(get_student.email, "Proposal request accepted.", message)

    return redirect(url_for('proposal.my_proposals'))


@proposal.route('/proposal-answer-reject', methods=['POST'])
def answer_proposal_reject():
    prop_id = request.form.get('proposal_id')
    my_proposal = Proposal.query.filter(Proposal.proposal_id == prop_id).first()
    my_proposal.is_accepted = "2"
    flash("You have successfully rejected student's proposal.", "danger")
    db.session.commit()

    get_student = User.query.filter(User.id == my_proposal.student_id).first()

    get_advisor = User.query.filter(User.id == my_proposal.advisor_id).first()

    message = "Your proposal declined by " + get_advisor.first_name + " " + get_advisor.last_name

    send_mail(get_student.email, "Proposal request declined.", message)

    return redirect(url_for('proposal.my_proposals'))
