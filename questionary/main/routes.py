from flask import (render_template, request, Blueprint,
                   redirect, url_for, jsonify, make_response)
from questionary.models import Category, Questions, Answer, User, SiteData
from questionary import db
from flask_login import current_user, login_required
import json

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
    # add new category mechanism handeling
    if request.method == 'POST':
        # get the form entries and remove the submit button entry
        results_dict = request.form.to_dict()
        results_dict.pop('submit')
        if current_user.is_authenticated:
            # get the id's of the categories marked in the form
            user_categories = set()
            for category in Category.query.all():
                # html form elements id's:
                category_check_box_id = f'category-{category.id}-checkbox'
                if category_check_box_id in results_dict:
                    # pop should retrieve the field data - the category id in our case
                    user_categories.add(
                        int(results_dict.pop(category_check_box_id)))
            print(results_dict)
            # the rest of the form entries are the questions themselfs
            for ((question_id, exp_value), (_, wil_value)) in grouped(results_dict.items()):
                question = Questions.query.get(question_id)
                answer = Answer(question=question, author=current_user,
                                exp_answer=exp_value, wil_answer=wil_value)
                db.session.add(answer)
            current_user.categories = list(user_categories)
            db.session.commit()
            return redirect(url_for('users.user_results', username=current_user.username))
    return redirect(url_for('main.questionary'))


@login_required
@main.route('/questionary', methods=['GET', 'POST'])
def questionary():
    categories = Category.query.order_by(Category.id).all()
    return render_template('questionary_with_jinja.html', categories=categories, user=current_user)
