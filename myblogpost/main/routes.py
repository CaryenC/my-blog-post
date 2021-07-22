# create user blueprint
from flask import render_template, request, Blueprint
from myblogpost.models import Post

main = Blueprint('main',__name__)

@main.route("/") # decoratory
@main.route("/home")
def home():
    '''
    Retrieve all saved posts
    :return render_template return home.html page
    '''
    page = request.args.get('page', 1, type=int)
    post = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', post=post)

@main.route("/about")
def about():
    '''
    Render about.html page
    :return render_template render about.html page
    '''
    return render_template('about.html', title='About')