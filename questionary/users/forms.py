from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, URL, Optional
from flask_login import current_user
from questionary.models import User
import requests


class RegistrationForm(FlaskForm):
    username = StringField('שם משתמש', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('אימייל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמה', validators=[DataRequired()])
    confirm_password = PasswordField('אישור סיסמה', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('הרשמה!')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('שם משתמש תפוס')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('המייל הזה כבר בשימוש')


class LoginForm(FlaskForm):
    email = StringField('מייל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמה', validators=[DataRequired()])
    remember = BooleanField('זכור אותי')
    submit = SubmitField('כניסה')


class UpdateAccountForm(FlaskForm):
    username = StringField('שם משתמש', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('מייל', validators=[DataRequired(), Email()])
    picture = FileField('תמונת פרופיל', validators=[
                        FileAllowed(['jpeg', 'jpg', 'png'])])
    submit = SubmitField('עדכון')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('שם משתמש תפוס')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('המייל הזה כבר בשימוש')


class RequestResetForm(FlaskForm):
    email = StringField('מייל', validators=[DataRequired(), Email()])
    submit = SubmitField('שלח מייל לאיפוס סיסמה')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('אין חשבון המשויך לכתובת המייל הזו!')


class RequestConfirmForm(FlaskForm):
    submit = SubmitField('שלחו מייל לאישור חשבון')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('סיסמה', validators=[DataRequired()])
    confirm_password = PasswordField('אישור סיסמה', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('שנה סיסמה')


class UpdateProfileForm(FlaskForm):
    gender = SelectField('מגדר', choices=[('גבר', 'גבר'), ('אישה', 'אישה'), ('א-מגדר', 'א-מגדר'),
                                          ('לא בינארי', 'לא בינארי'), ('אחר', 'אחר'), ('מעדיפים לא לומר', 'מעדיפים לא לומר')])
    show_gender = BooleanField('הראה מגדר')
    looking_for = SelectField('אני מחפש\\ת', choices=[('שולט\\ת', 'שולט\\ת'), (
        'בן\\בת זוג', 'בן\\בת זוג'), ('כלום', 'כלום'), ('חברים לחיים', 'חברים לחיים')])
    show_looking = BooleanField('הראה מה אני מחפש\\ת')
    about = TextAreaField('על עצמי')
    link = StringField('לינק לאתר אישי', validators=[Optional(), URL()])
    submit = SubmitField('עדכון')
