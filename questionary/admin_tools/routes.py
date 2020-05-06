from flask import render_template, flash, url_for, redirect, Blueprint
from flask_login import current_user, login_required
from questionary import db
from questionary.admin_tools.forms import NewCategoryForm, NewQuestionForm
from questionary.models import Category, Questions

admin_tools = Blueprint('admin_tools', __name__)


@admin_tools.route('/add_category', methods=['GET', 'POST'])
@login_required
def add_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash(f'הקטגוריה {form.name.data} הוספה!')
    return render_template('add_category.html', form=form)


@admin_tools.route('/add_question', methods=['GET', 'POST'])
@login_required
def add_question():
    form = NewQuestionForm()
    form.category.choices = [
        (category.name, category.name) for category in Category.query.all()]
    if form.validate_on_submit():
        question = Questions(question=form.question.data,
                             explanation=form.explanation.data,
                             category=Category.query.filter_by(name=form.category.data).first_or_404())
        db.session.add(question)
        db.session.commit()
        flash(f'השאלה {form.question.data} הוספה לקטגוריה {form.category.data}')
    return render_template('add_question.html', form=form)
