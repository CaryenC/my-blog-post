import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from myblogpost import mail

def save_picture(form_picture):
    '''
    Save user's uploaded profile picture in file system
    :param form_picture
    :return picture_fn return picture filename
    '''
    # set the picture file name randomly
    random_hex = secrets.token_hex(8)
    # save the original file extension
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    # get the uploaded picture oath
    picture_path = os.path.join(current_app.root_path,'static/profile_pics', picture_fn)
    # resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save the image
    i.save(picture_path)

    return picture_fn

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('MyBlogpost: Password Reset Request', 
                    sender='noreply@demo.com',
                    recipients=[user.email])
    # _external is to show the absolute path
    msg.body = '''\\To reset your password, visit the following link:
    {url_for('users.reset_token', token=token, _external=True)}

    If you did not make it request, simply ignore this email and no changes will be made.
    '''
    mail.send(msg)