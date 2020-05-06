import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from questionary import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_file_name = random_hex + file_ext
    picture_path = os.path.join(
        current_app.root_path, 'static/profile_pics', picture_file_name)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_file_name


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('בקשת איפוס סיסמה',
                  sender='matan.arielhavron1@gmail.com', recipients=[user.email])
    msg.body =\
        f'''כדי לאפס סיסמה בבקשה היכנסו לקישור הבא: 
{url_for('users.reset_token', token=token, _external=True)}
אם לא ביקשתם לאפס סיסמה, אתם יכולים להתעלם מהמייל.\n'''
    mail.send(msg)
