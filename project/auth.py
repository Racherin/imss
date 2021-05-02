from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Student, Advisor
from flask_login import login_user, login_required, logout_user

auth = Blueprint('auth', __name__)


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

    if str(email).endswith('@') or '@' not in str(email) or str(email).endswith('iyte.edu.tr') or str(
            email).strip() == '':
        flash('Please make sure that you enter valid mail.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist reload the page

    if usertype == 'student':
        user = Student.query.filter_by(email=email).first()
    elif usertype == 'advisor':
        user = Advisor.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        flash('Please check your email and try again.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist reload the page
    elif not check_password_hash(user.password, password):
        flash('Please check your password details and try again.')
        return redirect(url_for('auth.login'))  # if password is wrong, reload the page

    login_user(user, remember=remember)  # create user session

    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template("signup2.html")


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('first_name')
    password = request.form.get('password')
    password_check = request.form.get('password_check')
    usertype = request.form.get('usertype')

    if password_check != password:
        flash("Passwords do not match.")
        return redirect(url_for('auth.signup'))

    if usertype == 'student':
        user = Student.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = Student(email=email, first_name=name, password=generate_password_hash(password, method='sha256'))
    elif usertype == 'advisor':
        user = Advisor.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database
        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = Advisor(email=email, first_name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
