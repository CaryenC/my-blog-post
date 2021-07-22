# create user blueprint
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from myblogpost import db, bcrypt
from myblogpost.models import User, Post
from myblogpost.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from myblogpost.users.utils import save_picture, send_reset_email

users = Blueprint('users',__name__)

@users.route("/register", methods=['GET', 'POST'])
def register():
    '''
    Check if current user is authenticated, redirect the user to home page.
    Allow new users to register with username, email and hashed password
    And save these information in user table then redirect to login page.
    :return render_template render register.html page
    '''
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    '''
    Check if current user is authenticated, redirect the user to home page.
    Allow new users to login with email and password
    :return render_template render login.html page
    '''
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash(f'Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout", methods=['GET', 'POST'])
def logout():
    '''
    Log out current user, redirect the user to login page.
    :return render_template render logout.html page
    '''
    logout_user()
    return redirect(url_for('users.login'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    '''
    For authenticated user to update account information, redirect the user to account page.
    :return render_template render account.html page
    '''
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET': # but 
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.route("/user/<string:username>")
def user_posts(username):
    '''
    View all posts created by a specifc user
    :param username To view a specifc username's post
    :return render_template return user_posts.html page
    '''
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    post = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', post=post, user=user)

@users.route("/reset_password", methods=['GET','POST'])
def reset_request():
    '''
    Delete a specific post, redirect the user to home page.
    :param post_id the specific post ID
    :return render_template render logout.html page
    '''
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Check your inbox with instructions to reset your password.', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@users.route("/reset_password/<string:token>", methods=['GET','POST'])
def reset_token(token):
    '''
    Reset password with token active
    :param post_id the specific post ID
    :return render_template render logout.html page
    '''
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Your password has been reset! You can now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)    