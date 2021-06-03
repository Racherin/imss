from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_file, jsonify
from app import ALLOWED_EXTENSIONS
from models import Proposal, File, Uploads, User
from flask_login import current_user, login_required
from sqlalchemy import and_
from app import app
from flask_mail import Mail, Message
from webmail import send_mail
from app import db
import os
from obs import OBSWrapper
from werkzeug.exceptions import RequestEntityTooLarge

files = Blueprint('files', __name__)
mail = Mail(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
@files.route("/forms")
def forms():
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "0")).all()
    proposal_count = len(get_proposals)
    get_proposals = Proposal.query.filter(and_(Proposal.advisor_id == current_user.id,
                                               Proposal.is_accepted == "1")).all()

    root_path = str(current_app.root_path)

    submit_status = " "
    if current_user.advisor_id is None:
        submit_status = "disabled"

    form_list = File.query.filter().all()

    data = {
        'name': str(current_user.first_name).title() + ' ' + str(current_user.last_name).title(),
        'usertype': str(current_user.type_user).title(),
        'all_proposals': get_proposals,
        'proposal_count': proposal_count,
        'root_path': root_path,
        'submit_status': submit_status,
        'form_list': form_list,
        'user_photo': OBSWrapper(current_user.email).get_photo(),
        'advisor_status': ""
    }

    if current_user.advisor_id is None:
        flash("Submits are disabled, no advisor found!!!", "danger")
        data['advisor_status'] = "disabled"
        return render_template("forms.html", data=data)

    return render_template("forms.html", data=data)


@login_required
@files.route("/checkform")
def check_form():
    formtype = request.args.get('formtype', "0", type=str)
    formtype = formtype.strip()

    get_form_name = File.query.filter(File.form_type == formtype).first()

    check_form = Uploads.query.filter(and_(Uploads.student_id == current_user.id,
                                           Uploads.form_id == get_form_name.id)).first()

    check_advisor_status = current_user.advisor_id

    if check_advisor_status is None:
        return jsonify({'status': 'undefined', 'formname': ""})

    if check_form is None:
        return jsonify({'status': 'false', 'formname': ""})
    else:
        print(check_form.file_name)
        return jsonify({'status': 'true', 'formname': check_form.file_name})


@login_required
@files.route('/download/<file>', methods=['GET'])
def downloadFile(file):
    file = "/uploads/" + file
    path = current_app.root_path + file
    return send_file(path, as_attachment=True)


@login_required
@files.route('/downloadfile/<stid>/<file>', methods=['GET'])
def downloadUploadedFile(file, stid):
    get_form_name = File.query.filter(File.form_name == file).first()

    get_form = Uploads.query.filter(and_(Uploads.student_id == str(stid).strip(),
                                         Uploads.form_id == get_form_name.id)).first()

    file = "/media/" + stid + "/" + get_form.file_name
    path = current_app.root_path + file
    return send_file(path, as_attachment=True)



@login_required
@files.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files['file']

        blob = request.files['file'].read()
        size = len(blob)

        if size > 5000000:
            flash("File size is exceeded!", "danger")
            return redirect(url_for('files.forms'))

        form_name = request.form.get('form-name')
        file_path = "media/" + str(current_user.id) + "/" + uploaded_file.filename

        try:
            if uploaded_file and allowed_file(uploaded_file.filename):
                uploaded_file.save(dst="media/" + str(current_user.id) + "/" + uploaded_file.filename)
            else:
                flash("Please upload supported file types. Only supported file type is PDF !", "danger")
                return redirect(url_for('files.forms'))
        except Exception as e:
            print(e)
            flash("An error occured while uploading the file!\nPlease try again!", "danger")
            return redirect(url_for("files.forms"))

        get_uploaded_form_id = File.query.filter(File.form_name == form_name).first()
        new_upload = Uploads(form_id=get_uploaded_form_id.id, student_id=current_user.id, is_checked=False,
                             file_path=file_path, file_name=uploaded_file.filename, form_name=form_name)

        db.session.add(new_upload)
        db.session.commit()
        flash("File upload successfull", "success")

        get_student_advisor = User.query.filter(User.id == current_user.advisor_id).first()

        send_mail(current_user.email, "File Upload",
                  'Dear ' + current_user.first_name + " " + current_user.last_name + ',\nYour file ' + uploaded_file.filename + ' submission is successfull.\nIZTECH Master\'s Student System 2021\n')
        send_mail(get_student_advisor.email, "File Upload",
                  'Dear ' + get_student_advisor.first_name + " " + get_student_advisor.last_name + ',\nYour student ' + current_user.first_name + " " + current_user.last_name + '\'s file ' + uploaded_file.filename + ' is successfully submitted to the system.\nIZTECH Master\'s Student System 2021\n')

        return redirect(url_for("files.forms"))


@login_required
@files.route('/delete_item/<form_name>/', methods=['GET', 'POST'])
def delete_item(form_name):
    get_form_name = File.query.filter(File.form_name == form_name).first()

    get_form = Uploads.query.filter(and_(Uploads.student_id == current_user.id,
                                         Uploads.form_id == get_form_name.id)).first()

    file_path = "/media/" + str(current_user.id) + "/" + get_form.file_name

    os.remove(current_app.root_path + file_path)

    db.session.delete(get_form)
    db.session.commit()

    flash("Form is deleted", "info")
    return redirect(url_for('files.forms'))
