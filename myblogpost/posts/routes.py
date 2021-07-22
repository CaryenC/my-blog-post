# create user blueprint
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from myblogpost import db
from myblogpost.models import Post
from myblogpost.posts.forms import PostForm

posts = Blueprint('posts',__name__)

@posts.route("/post/new", methods=['GET', 'POST'])
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
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@posts.route("/post/<int:post_id>")
def post(post_id):
    '''
    Retrieve a specific post, redirect the user to the post page.
    :param post_id the specific post ID
    :return render_template render post.html page
    '''
    post = Post.query.get_or_404(post_id)  # Post.query.get(post_id)
    return render_template('post.html', title= post.title, post=post)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
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
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET': # but 
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title= "Update Post", form=form, legend='Update Post')

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
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
    return redirect(url_for('main.home'))
