from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from os.path import join, dirname, realpath

"""
This file includes initialization of database and base application of flask web server.
In the preceding code block, you first import the Flask object from the flask package. 
Then use it to create your Flask application instance with the name app. 
You pass the special variable __name__ that holds the name of the current Python module. 
It’s used to tell the instance where it’s located.
"""

UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'media')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)


@app.errorhandler(404)
# inbuilt function which takes error as parameter
def not_found(e):
    # defining function
    return render_template("404.html")




app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = "/media/"
#app.config['MAX_CONTENT_LENGTH'] = 1 * 1000 * 1000


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'imssconfirm@gmail.com'
app.config['MAIL_PASSWORD'] = 'Asdasd123.'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

s = URLSafeTimedSerializer('Thisisasecret!')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)
app.permanent_session_lifetime = timedelta(minutes=60)

from models import User


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))


# blueprint for auth routes in our app
from auth import auth as auth_blueprint

app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from main import main as main_blueprint

app.register_blueprint(main_blueprint)

from files import files as files_blueprint

app.register_blueprint(files_blueprint)

from proposal import proposal as proposal_blueprint

app.register_blueprint(proposal_blueprint)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
