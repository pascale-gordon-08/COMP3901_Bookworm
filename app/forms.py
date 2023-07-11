from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField, BooleanField, validators
from wtforms.validators import InputRequired, Length, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed


class UploadForm(FlaskForm):
    pdf = FileField('PDF', validators=[FileRequired(), FileAllowed(['pdf'], 'Only PDF files are allowed!')])

class RegistrationForm(FlaskForm):
    fname = StringField('Firstname', validators=[InputRequired()])
    lname = StringField('Lastname', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
      
    
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    
    

class ChatForm(FlaskForm):
    query = TextAreaField('Enter Query')
    