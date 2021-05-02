from flask import Blueprint, render_template, request, redirect, url_for
from . import db
from flask_login import login_required, current_user
from .models import User, Proposal

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template("login2.html")


@main.route('/dashboard')
@login_required
def dashboard():
    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
    }
    return render_template("dashboard.html", data=data)


@main.route('/propose-advisor')
@login_required
def propose_advisor():
    all_advisors = User.query.filter(User.type_user == 'advisor').all()
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
    thesis_topic = request.form.get('thesistopic')
    new_proposal = Proposal(student_id=studentid,advisor_id=advisorid,thesis_topic=thesis_topic)
    db.session.add(new_proposal)
    db.session.commit()
    return redirect(url_for('main.dashboard'))
