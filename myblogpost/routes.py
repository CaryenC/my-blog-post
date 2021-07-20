# Import libraries
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort 
from myblogpost import app, db, bcrypt
from myblogpost.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from myblogpost.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

# Create different endpoints
@app.route("/") # decoratory
@app.route("/home")
def home():
    '''
    Retrieve all saved posts
    :return render_template return home.html page
    '''
    page = request.args.get('page', 1, type=int)
    post = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', post=post)

@app.route("/about")
def about():
    '''
    Render about.html page
    :return render_template render about.html page
    '''
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    '''
    Check if current user is authenticated, redirect the user to home page.
    Allow new users to register with username, email and hashed password
    And save these information in user table then redirect to login page.
    :return render_template render register.html page
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You can now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    '''
    Check if current user is authenticated, redirect the user to home page.
    Allow new users to login with email and password
    :return render_template render login.html page
    '''
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash(f'Login unsuccessful. Please check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    '''
    Log out current user, redirect the user to login page.
    :return render_template render logout.html page
    '''
    logout_user()
    return redirect(url_for('login'))

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
    picture_path = os.path.join(app.root_path,'static/profile_pics', picture_fn)
    # resize the image
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    # save the image
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET': # but 
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

'''
Route for inputting more posts automatically

@app.route("/post/json/")
def post_json():
    ###   
    To insert a JSON data into SQLAlchemy Post table
    :param data A set of post data in JSON format
    ###
    posts_entries = []
    for posts in data["all_posts"]:
        new_post = Post(title=posts['title'], content=posts['content'], user_id=posts['user_id'])
        posts_entries.append(new_post)
    db.session.add_all(posts_entries)
    db.session.commit()
    flash('Your JSON post has been created!', 'success')
    return redirect(url_for('home'))
'''

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def post_new():
    '''
    Allow current user to post new post, redirect the user to home page.
    :return render_template render create_post.html page
    '''
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route("/post/<int:post_id>")
def post(post_id):
    '''
    Retrieve a specific post, redirect the user to the post page.
    :param post_id the specific post ID
    :return render_template render post.html page
    '''
    post = Post.query.get_or_404(post_id)  # Post.query.get(post_id)
    return render_template('post.html', title= post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    '''
    Update posts, redirect the user to post page.
    :param post_id the specific post ID
    :return render_template render create_post.html page
    '''
    post = Post.query.get_or_404(post_id)  # Post.query.get(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET': # but 
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title= "Update Post", form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    '''
    Delete a specific post, redirect the user to home page.
    :param post_id the specific post ID
    :return render_template render logout.html page
    '''
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/user/<string:username>")
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