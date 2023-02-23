from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Character

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UserRegistrationForm(FlaskForm):
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).one_or_none()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).one_or_none()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_character(self, name):
        char = Character.query.filter_by(name=name.data).one_or_none()
        if char is not None:
            raise ValidationError('Please use a different character name.')
        
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Character Name', validators=[DataRequired(), validate_character])   
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Register User')



class EditProfileForm(FlaskForm):

    def __init__(
        self, original_username,
        original_char_name,
        original_char_level,
        original_char_speed, 
        *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_char_name = original_char_name
        self.original_char_level = original_char_level
        self.original_char_speed = original_char_speed
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')   
   
    def validate_char_name(self, char_name):
        if char_name.data != self.original_char_name:
            char = Character.query.filter_by(name=self.char_name.data).first()
            if char is not None:
                raise ValidationError('Please use a different character name.')   

    username = StringField('Username', validators=[DataRequired()])
    char_name = StringField('Character Name', validators=[DataRequired()])
    char_level = IntegerField('Character level')
    char_speed = IntegerField('Character speed')
    submit = SubmitField('Submit')

class ArticleForm(FlaskForm):
    headline = StringField('headline', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')
