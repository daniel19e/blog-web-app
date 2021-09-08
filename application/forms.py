from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from application.models import User


class Register(FlaskForm):
    """This is a database model
     that allows users to register"""

    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5)])

    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Register')

    def validate_username(self, username):
        """Checks if username is already in the database"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken')

    def validate_email(self, email):
        """Checks if email is already in the database"""
        email_address = User.query.filter_by(email=email.data).first()
        if email_address:
            raise ValidationError('Email already registered')

class Login(FlaskForm):
    """This is a database model
    that allows users to login"""

    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

    remember_user = BooleanField('Remember User')

    submit = SubmitField('Login')


class UpdateAccountInfo(FlaskForm):
    """This is a database model
     that allows users to update their information"""

    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    prof_pic = FileField('Update Profile Picture', validators=[FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        """Checks if username is already in the database"""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken')

    def validate_email(self, email):
        """Checks if email is already in the database"""
        if email.data != current_user.email:
            email_address = User.query.filter_by(email=email.data).first()
            if email_address:
                raise ValidationError('Email already registered')


class Post(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')