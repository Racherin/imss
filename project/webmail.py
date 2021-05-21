from flask_mail import Mail, Message
from app import app

mail = Mail(app)

def send_mail(to,title,context):
    msg = Message(title, sender='imssconfirm@gmail.com', recipients=[to])
    msg.body = context
    mail.send(msg)
