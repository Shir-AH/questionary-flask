from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from questionary import db, bcrypt
from questionary.models import User, QuestionaryResults
from questionary.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                     RequestResetForm, ResetPasswordForm, RequestConfirmForm)
from questionary.users.utils import (
    save_picture, send_reset_email, send_confirm_email, restricted)
import json
from datetime import datetime as dt

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_pw, confirmed=False)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(
            f'חשבון נוצר בעבור {form.username.data}.\nאנא אשרו את המשתמש באמצעות המייל שקיבלתם', 'success')
        return redirect(url_for('main.home'))
    return render_template('register.html', title='הרשמה', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('סיסמה או מייל לא נכונים, נסו שוב.', 'danger')
    return render_template('login.html', title='כניסה', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
@restricted(access_level='confirmed')
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('החשבון שלך עודכן', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for(
        'static', filename=f'profile_pics/{current_user.image_file}')
    return render_template('account.html', title='חשבון', image_file=image_file, form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('בדקו את המייל שלכם!', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form)


@users.route('/confirm_account', methods=['GET', 'POST'])
@login_required
def request_confirm_account():
    if current_user.is_confirmed:
        flash('החשבון הזה כבר מאושר :)', 'info')
        return redirect(url_for('main.home'))
    form = RequestConfirmForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        send_confirm_email(user)
        flash('בדקו את המייל שלכם!', 'info')
        return redirect(url_for('main.home'))
    return render_template('confirm_request.html', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_token(token=token)
    if user is None:
        flash('הקוד לא נכון\לא תקף. בבקשה נסו שוב.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(
            f'{user.username}, הסיסמה שלך השתנתה! עכשיו אפשר להיכנס!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', form=form)


@users.route('/confirm_account/<token>', methods=['GET', 'POST'])
def confirm_token(token):
    if current_user.is_authenticated and current_user.is_confirmed:
        return redirect(url_for('main.home'))
    user = User.verify_token(token=token)
    if user is None:
        flash('הקוד לא נכון\לא תקף. בבקשה נסו שוב.', 'warning')
        return redirect(url_for('users.request_confirm_account'))
    user.confirmed = True
    user.confirmed_on = dt.now()
    db.session.commit()
    flash('החשבון שלך מאושר!', 'success')
    return redirect(url_for('main.home'))


@users.route('/please_confirm')
def confirmation_needed():
    return render_template('confirmation_needed.html')


@users.route('/user/<string:username>')
def user_results(username):
    user = User.query.filter_by(username=username).first_or_404()
    result_id = QuestionaryResults.query.filter_by(author=user).order_by(
        QuestionaryResults.date_posted.desc()).first_or_404().id
    return redirect(url_for('main.answers', id=result_id))


@users.route('/user/user_answer_id', methods=['GET', 'POST'])
def get_current_user_answer_id():
    if current_user.is_authenticated:
        answer_id = QuestionaryResults.query.filter_by(author=current_user).order_by(
            QuestionaryResults.date_posted.desc()).first_or_404().id
    else:
        answer_id = -1
    return jsonify(answer_id)
