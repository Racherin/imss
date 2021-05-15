from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_file
from werkzeug.utils import secure_filename
from app import ALLOWED_EXTENSIONS
from models import Proposal
from flask_login import current_user
from sqlalchemy import and_
from app import app
from flask_mail import Mail, Message

files = Blueprint('files', __name__)
mail = Mail(app)


@files.route("/forms")
def forms():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "1")).all()

    root_path = str(current_app.root_path)
    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count,
        'root_path': root_path

    }
    return render_template("forms.html", data=data)


@files.route('/download/<file>', methods=['GET'])
def downloadFile(file):
    file = "/uploads/" + file
    path = current_app.root_path + file
    return send_file(path, as_attachment=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@files.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        try:
            uploaded_file.save(dst="media/" + str(current_user.id) + "/" + uploaded_file.filename)
        except Exception as e:
            flash("An error occured while uploading the file!\nPlease try again!", "danger")
            return redirect(url_for("files.forms"))

        flash("File upload successfull", "success")

        msg = Message('File upload', sender='imssconfirm@gmail.com', recipients=[current_user.email])
        msg.body = 'Dear ' + current_user.first_name + " " + current_user.last_name + ',\nYour file ' + uploaded_file.filename + \
                   ' submission is successfull.\nIZTECH Master\'s Student System 2021\n'
        mail.send(msg)

        return redirect(url_for("files.forms"))
