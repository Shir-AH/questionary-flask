from flask import Flask, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.fields.html5 import IntegerRangeField

app = Flask(__name__)
app.secret_key = 'secret'


class Category(object):
    def __init__(self, name):
        self.name = name


class Question(object):
    def __init__(self, name, value, category):
        self.name = name
        self.value = value
        self.category = category


c1 = Category('c1')
c2 = Category('c2')
q1 = Question('q1', 'askme', c1)
q2 = Question('q2', 'askme', c1)
q3 = Question('q3', 'askme', c1)
q4 = Question('q4', 'askme', c2)
q5 = Question('q5', 'askme', c2)
q6 = Question('q6', 'askme', c2)


categories = [c1, c2]
data = [q1, q2, q3, q4, q5, q6]


class emptyParentForm(FlaskForm):
    """A general parent form class that is created statically is needed
    in order for dynamically created forms to work."""
    pass


@app.route('/', methods=['GET', 'POST'])
def displayPage():
    # This subclass is necessary to dynamically add fields to the form
    class dynmicForm(emptyParentForm):
        pass

    # Dynmanically Setting the form fields
    for question in data:
        setattr(
            dynmicForm, f'{question.name}:{question.category.name}:wil', IntegerRangeField())
        setattr(
            dynmicForm, f'{question.name}:{question.category.name}:exp', IntegerRangeField())

    # Creating the form object
    form = dynmicForm()
    return render_template('main.html', form=form, legend='שמחה', data=data, categories=categories)
