from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from myblogpost import db, login_manager
from flask_login import UserMixin # for current_user

# load logged-in user id in a session variable
@login_manager.user_loader # must use this naming convention to tell LoginManager this is the function to get user id
def load_user(user_id):
    return User.query.get(int(user_id))

# Classes to define tables inheriting from db.Model class
# Table 1: Class User
class User(db.Model, UserMixin):
    # add columns for User table
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg') # going to hash these image files
    password = db.Column(db.String(60), nullable=False) # going to hash

    # table relationship
    '''
    :param posts has relationship with Post model
    :param backref add author column in Post module
    :param lazy data is neccessary or not
    '''
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod # not expecting 'self' as the argument
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        try:
            user_id = s.loads(token)['user_id']
        except: # if get exception
            return None
        return User.query.get(user_id) # else
    
    ## double underscore method / magic method
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

# Table 2: Class Post
class Post(db.Model):
    # add columns for User table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # use UTC for consistency purpose
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    # user from user.id is lowercase because we are referring to the table in this case, not the class name

    ## double underscore method / magic method
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"