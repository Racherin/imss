from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, Department, Proposal
from flask_login import login_user, login_required, logout_user, current_user
import re
from obs import OBSWrapper
from app import s, app
from flask_mail import Message, Mail
from itsdangerous import SignatureExpired
import os
from sqlalchemy import and_


"""

This file includes some examples of how to handle HTTP requests about authentication process.
Once we create the app instance before in the app.py file, we'll use it to handle incoming web requests and send 
responses to the user.
@app.route is a decorator that turns a regular Python function into a Flask view function, which converts the function’s
return value into an HTTP response to be displayed by an HTTP client, such as a web browser. 

"""

auth = Blueprint('auth', __name__)
mail = Mail(app)



@auth.route('/login')
def login():
    return render_template("login2.html")


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    usertype = request.form.get('usertype')
    remember = True if request.form.get('remember') else False
    user = None

    if str(email).endswith('@') or '@' not in str(email) or not str(email).endswith('iyte.edu.tr') or not str(
            email).endswith('iyte.edu.tr') or str(email).strip() == '':
        flash('Please make sure that you enter valid mail.', "danger")
        return redirect(url_for('auth.login'))  # if the user doesn't exist reload the page

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database

    if not user:
        flash('Please check your email and try again.', "danger")
        return redirect(url_for('auth.login'))  # if the user doesn't exist reload the page
    elif not check_password_hash(user.password, password):
        flash('Please check your password details and try again.', "danger")
        return redirect(url_for('auth.login'))  # if password is wrong, reload the page

    if user.confirmed != True:
        flash("Please activate your account.", "success")
        return redirect(url_for("auth.login"))

    login_user(user, remember=remember)  # create user session

    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.dashboard'))


@auth.route('/forgotpassword')
def forgot_password():
    return render_template("forgotpassword.html")


@auth.route('/forgotpassword', methods=["POST"])
def forgot_password_post():
    email = request.form.get('email')

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash("Please enter valid email", "danger")
        return redirect(url_for("auth.forgot_password"))
    else:
        token = s.dumps(email, salt='forgot-password')
        msg = Message('Forgot Password', sender='imssconfirm@gmail.com', recipients=[email])
        link = url_for('auth.reset_password', token=token, _external=True)
        msg.body = 'Please click here to reset your password {}'.format(link)
        mail.send(msg)
        flash("Please check your mailbox to reset password.", "success")

        return redirect(url_for("auth.forgot_password"))


@auth.route('/resetpassword/<token>')
def reset_password(token):
    try:
        email = s.loads(token, salt='forgot-password', max_age=600)
    except SignatureExpired:
        flash("Activation token expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(
        email=email).first()

    data = {
        "email": user.email,
    }
    return render_template("resetpassword.html", data=data)


@auth.route('/resetpassword', methods=["POST"])
def reset_password_post():
    email = request.form.get("email")
    new_password = request.form.get("password")
    new_password_check = request.form.get("password_check")


    reg_notwork = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-.]).{8,12}$"
    pat = re.compile(reg_notwork)
    mat = re.search(pat, new_password)

    if not mat:
        flash("Your password cannot be this" "danger")
        return redirect(url_for("auth.reset_password"))

    if not new_password == new_password_check:
        flash("Your new passwords do not match!", "danger")
        return redirect("auth.reset_password")

    print(email)
    user = User.query.filter_by(email=email).first()

    user.password = generate_password_hash(new_password, method='sha256')

    db.session.commit()
    flash("Password change successfull", "success")
    return redirect(url_for("auth.login"))


@auth.route('/signup')
def signup():
    return render_template("signup2.html")


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    password = request.form.get('password')
    password_check = request.form.get('password_check')
    reg_notwork = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-.]).{8,12}$"
    pat = re.compile(reg_notwork)
    mat = re.search(pat, password)

    if not mat:
        flash("Invalid password format!", "danger")
        return redirect(url_for("auth.signup"))

    if str(email).endswith('@') or '@' not in str(email) or not str(email).endswith('iyte.edu.tr') or str(
            email).strip() == '':
        flash('Please make sure that you enter valid mail.', "danger")
        return redirect(url_for('auth.signup'))  # if the user doesn't exist reload the page

    if password_check != password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('auth.signup'))

    try :
        new_user = OBSWrapper(email)
    except KeyError :
        flash("This email does not exists on the system.")
        return redirect(url_for("auth.signup"))

    if new_user.response == "error":
        flash("This user does not exists.", "danger")
        return redirect(url_for('auth.signup'))

    first_name = " ".join(str(new_user.get_user_name()).split()[0:-1])
    last_name = str(new_user.get_user_name()).split()[-1]

    usertype = new_user.get_user_type()

    if usertype == "Student":
        user = User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists', "danger")
            return redirect(url_for('auth.signup'))

        department = Department.query.filter(Department.dept_name == new_user.get_user_department()).first()

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email,
                           type_user='student',
                           password=generate_password_hash(password, method='sha256'),
                           first_name=first_name,
                           last_name=last_name,
                           dept_id=department.dept_id)
    elif usertype == "Advisor":
        user = User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists', "danger")
            return redirect(url_for('auth.signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        department = Department.query.filter(Department.dept_name == new_user.get_user_department()).first()

        new_user = User(email=email,
                           type_user='student',
                           password=generate_password_hash(password, method='sha256'),
                           first_name=first_name,
                           last_name=last_name,
                           dept_id=department.dept_id)
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    token = s.dumps(email, salt='email-confirm')
    msg = Message('Confirm Email', sender='imssconfirm@gmail.com', recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = 'Your link is {}'.format(link)
    mail.send(msg)


    get_user = User.query.filter(User.email == email).first()
    os.makedirs(current_app.root_path + "/media/" + str(get_user.id))
    flash("You are signed up successfully we have sent you a confirmation  email", 'success')
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.index'))


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        flash("Activation token expired.", "danger")
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(
        email=email).first()

    user.confirmed = True

    db.session.commit()
    flash("Activation succesfull !", "success")
    return redirect(url_for("auth.login"))


@auth.route('/updatepassword')
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
        'proposal_count': proposal_count,
        'user_photo': OBSWrapper(current_user.email).get_photo(),

    }

    return render_template("updatepassword.html", data=data)


@auth.route("/updatepassword", methods=['POST'])
def update_password_post():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    new_password_again = request.form.get("new_password2")

    reg_notwork = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-.]).{8,12}$"
    pat = re.compile(reg_notwork)
    mat = re.search(pat, new_password)

    if not mat:
        flash("Your password cannot be this" "danger")
        return redirect(url_for("main.update_password"))

    if not new_password == new_password_again:
        flash("Passwords are not match.", "danger")
        return redirect(url_for("main.update_password"))

    user = User.query.filter_by(
        email=current_user.email).first()

    if not check_password_hash(user.password, current_password):
        flash("Please enter correct password", "danger")
        return redirect(url_for("main.update_password"))

    user.password = generate_password_hash(new_password)

    db.session.commit()

    flash("Password change successfull", "success")
    return redirect(url_for("main.update_password"))


