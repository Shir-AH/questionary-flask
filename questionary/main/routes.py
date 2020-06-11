from flask import (render_template, request, Blueprint,
                   redirect, url_for, jsonify, make_response)
from questionary.models import Category, Questions, Answer, User, SiteData
from questionary import db
from flask_login import current_user, login_required
import json
# import pdfkit

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('main.html', site_data=SiteData.data_dict())


def grouped(iterable, n=2):
    return zip(*[iter(iterable)]*n)


@login_required
@main.route('/submit_questionary', methods=['POST'])
def submit_questionary():
    if request.method == 'POST':
        results_dict = request.form.to_dict()
        if current_user.is_authenticated:
            user_categories = set()
            for ((question_id, exp_value), (_, wil_value)) in grouped(results_dict.items()):
                question = Questions.query.get(question_id)
                user_categories.add(question.category.id)
                answer = Answer(question=question, author=current_user,
                                exp_answer=exp_value, wil_answer=wil_value)
                db.session.add(answer)
            print(list(user_categories))
            current_user.categories = list(user_categories)
            db.session.commit()
            return redirect(url_for('users.user_results', username=current_user.username))
    return redirect(url_for('main.questionary'))


@login_required
@main.route('/questionary', methods=['GET', 'POST'])
def questionary():
    categories = Category.query.all()
    return render_template('questionary_with_jinja.html', categories=categories, user=current_user)
