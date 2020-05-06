from flask import render_template, request, Blueprint
from questionary.models import QuestionaryResults

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    return render_template('main.html')


@main.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        results = request.form.to_dict()
        print(results)
    return render_template('check.html', results=results)
