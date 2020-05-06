from flask import render_template, request, Blueprint, redirect, url_for, jsonify
from questionary.models import QuestionaryResults, Category, Questions
from questionary import db
from flask_login import current_user
import json

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('main.html')


@main.route('/questionary', methods=['GET', 'POST'])
def questionary():
    if current_user.is_authenticated:
        try:
            result_object = QuestionaryResults.query.filter_by(author=current_user).order_by(
                QuestionaryResults.date_posted.desc()).first_or_404()
            result_json_str = json.loads(result_object.questionary_results)
            return render_template('questionary.html', results=result_json_str)
        except:
            pass
    return render_template('questionary.html')


@main.route('/check', methods=['POST'])
def check():
    if request.method == 'POST':
        results_str = json.dumps(request.form.to_dict())
        if current_user.is_authenticated:
            results = QuestionaryResults(
                questionary_results=results_str, author=current_user)
        results = QuestionaryResults(questionary_results=results_str)
        db.session.add(results)
        db.session.commit()
        return redirect(url_for('main.answer_by_id', id=results.id))
    else:
        if current_user.is_authenticated:
            return redirect(url_for('user.user_results', username=current_user.username))
        else:
            return redirect(url_for('main.home'))


@main.route('/answer/<int:id>')
def answer_by_id(id):
    result_object = QuestionaryResults.query.filter_by(id=id).first_or_404()
    result_str = json.loads(result_object.questionary_results)
    return render_template('check.html', results=result_str, result_object=result_object)


@main.route('/questions', methods=['GET'])
def questions():
    questions_obj = {'data': []}

    categories = Category.query.all()
    for category in categories:
        category_questions = Questions.query.filter_by(category=category)

        category_obj = {
            'name': category.name,
            'questions': [{
                'question': q.question,
                'explanation': q.explanation
            } for q in category_questions]
        }

        questions_obj['data'].append(category_obj)

    return jsonify(questions_obj)
