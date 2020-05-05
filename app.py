from flask import Flask, render_template, url_for, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField
from wtforms.fields.html5 import IntegerRangeField

app = Flask(__name__)
app.secret_key = 'secret'


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main.html')


@app.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        results = request.form.to_dict()
        print(results)
    return render_template('check.html', results=results)
