from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp, Length

class SignupForm(FlaskForm):
    first_name = StringField('First Name:', validators=[
        DataRequired("Please enter your first name."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    last_name = StringField('Last Name:', validators=[
        DataRequired("Please enter your last name."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    email = StringField('Email:', validators=[
        DataRequired("Please enter your email address."),
        Email("The email you entered is invalid."),
        Length(max=100, message="This field has a 100 character limit.")])
    username = StringField('Username:', validators=[
        DataRequired("Please enter a username."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    password = PasswordField('Password:', validators=[
        DataRequired("Please enter a password.")])
    confirm = PasswordField('Confirm Password:', validators=[
        DataRequired("Please enter a password."),
        EqualTo('password', message='Your password confirmation did not match.')])
    submit = SubmitField('Sign Me Up!')

class SigninForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired("Please enter your email address."),
        Email("The email you entered is invalid."),
        Length(max=100, message="This field has a 100 character limit.")])
    password = PasswordField('Password:', validators=[DataRequired("Please enter a password.")])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name:', validators=[
        DataRequired("Please enter your first name."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    last_name = StringField('Last Name:', validators=[
        DataRequired("Please enter your last name."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    email = StringField('Email:', validators=[
        DataRequired("Please enter your email address."),
        Email("The email you entered is invalid."),
        Length(max=100, message="This field has a 100 character limit.")])
    username = StringField('Username:', validators=[
        DataRequired("Please enter a username."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    create_ts = DateTimeField('Member Since:')
    submit = SubmitField('Update')

class LeagueProfile(FlaskForm):
    league_id = StringField('League:', validators=[
        DataRequired("Please enter your first name."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    league_name = StringField('League:', validators=[
        DataRequired("Please enter your first name."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    league_owner = StringField('Owner:', validators=[
        DataRequired("Please enter your email address."),
        Email("The email you entered is invalid."),
        Length(max=100, message="This field has a 100 character limit.")])
    create_ts = DateTimeField('Created:')
    members_cnt = StringField('Members:', validators=[
        DataRequired("Please enter your email address."),
        Regexp("^[\w\-]+$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])

class LeaguePwd(FlaskForm):
    password = StringField('Password:', validators=[
        Length(max=100, message="This field has a 100 character limit.")])
    submit = SubmitField('Join')

class CreateLeague(FlaskForm):
    league_name = StringField('League Name:', validators=[
        DataRequired("Please enter your league name."),
        Length(max=100, message="This field has a 100 character limit.")])
    league_pwd = StringField('Password (optional):', validators=[
        Regexp("^[\w\-]*$", message="Special characters are not allowed."),
        Length(max=100, message="This field has a 100 character limit.")])
    submit = SubmitField('Create')

class CreateSquad(FlaskForm):
    squad_name = StringField('League Name:', validators=[
        DataRequired("Please enter your league name."),
        Length(max=100, message="This field has a 100 character limit.")])
    squad_pwd = StringField('Password (optional):', validators=[
        Length(max=100, message="This field has a 100 character limit.")])
    submit = SubmitField('Create')

class SubmitEmail(FlaskForm):
    email = StringField('Email:', validators=[
        DataRequired("Please enter your email address."),
        Email("The email you entered is invalid."),
        Length(max=100, message="This field has a 100 character limit.")])
    submit = SubmitField('Submit')

class PwdEmail(FlaskForm):
    email = StringField('Email:', validators=[
        DataRequired("Please enter your email address."),
        Email("The email you entered is invalid."),
        Length(max=100, message="This field has a 100 character limit.")])
    reset_token = StringField('Reset Token:', validators=[
        DataRequired("Please enter your last name."),
        Length(max=20, message="This field has a 20 character limit.")])
    password = PasswordField('New Password:', validators=[DataRequired("Please enter a password.")])
    confirm = PasswordField('Confirm Password:', validators=[
        DataRequired("Please enter a password."),
        EqualTo('password', message='Your password confirmation did not match.')])
    submit = SubmitField('Submit')

class PwdSession(FlaskForm):
    current = PasswordField('Current Password:', validators=[DataRequired("Please enter a password.")])
    new = PasswordField('New Password:', validators=[DataRequired("Please enter a password.")])
    confirm = PasswordField('Confirm New Password:', validators=[
        DataRequired("Please enter a password."),
        EqualTo('password', message='Your password confirmation did not match.')])
    submit = SubmitField('Submit')
