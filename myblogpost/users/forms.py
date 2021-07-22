from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from myblogpost.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[
                                DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', 
                            validators=[
                                DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')
    
    # custom validation
    def validate_username(self, username):
        '''
        Validate username from a given username
        :param username: username in registration form
        '''
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken. Please choose another one.')

    def validate_email(self, email):
        '''
        Validate email from a given email
        :param email: email in registration form
        '''
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is taken. Please choose another one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
            
    # empty input
    # character limit
    # secret key - prevent CSRF and 

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                            validators=[
                                DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                            validators=[
                                DataRequired(), Email()])

    picture = FileField('Update Profile Picture',
                            validators=[
                                FileAllowed(['jpg', 'png', 'jpeg'])])
                                
    submit = SubmitField('Update')
    
    # custom validation
    def validate_username(self, username):
        '''
        Validate username from a given username
        :param username: username in registration form
        '''
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first() # SQLAlchemy query statement
            if user:
                raise ValidationError('Username is taken. Please choose another one.')

    def validate_email(self, email):
        '''
        Validate email from a given email
        :param email: email in registration form
        '''
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is taken. Please choose another one.')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset Password')

    def validate_email(self, email):
        '''
        Validate email from a given email
        :param email: email in registration form
        '''
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('"If an account with this email address exists, a password reset message will be sent shortly.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                            validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')            