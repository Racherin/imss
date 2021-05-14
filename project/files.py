from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory, \
    send_file
from models import Proposal
from flask_login import current_user
from sqlalchemy import and_
import os, sys
from app import app

files = Blueprint('files', __name__)


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


@files.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)


@files.route('/download/<file>', methods=['GET'])
def downloadFile(file):
    print(123412)
    path = os.path.join(current_app.root_path, file)
    return send_file(path, as_attachment=True)
