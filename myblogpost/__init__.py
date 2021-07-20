# initialize our application
# bring different components here

# Import libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize the Flask app
app = Flask(__name__)

# Identify the what configuration this app needs
app.config['SECRET_KEY'] = '88a93c9a655ba86695c36fb864e51a1eb80ee87541ec2362d332a59604c25f34'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # the site.db is a db file, create in this same directory
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # function name of our route
login_manager.login_message_category = 'info' # Bootstrap's info 

from myblogpost import routes