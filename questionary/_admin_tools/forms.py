from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from flask_login import current_user
from questionary.models import Questions, Category


class NewQuestionForm(FlaskForm):
    category = SelectField('קטגוריה', choices=[], validators=[DataRequired()])
    question = StringField('שאלה', validators=[DataRequired()])
    explanation = TextField('הסבר')
    submit = SubmitField('הוספה')

    def validate_question(self, question):
        question = Questions.query.filter_by(question=question.data).first()
        if question:
            raise ValidationError('כבר יש שאלה כזאת :)')


class NewCategoryForm(FlaskForm):
    name = StringField('קטגוריה', validators=[DataRequired()])
    submit = SubmitField('הוספה')

    def validate_name(self, name):
        name = Category.query.filter_by(name=name.data).first()
        if name:
            raise ValidationError('כבר יש קטגוריה כזאת :)')
