from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify, make_response, abort
from flask_login import login_user, current_user, logout_user, login_required
from questionary import db, bcrypt
from questionary.models import User, Category
from questionary.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                     RequestResetForm, ResetPasswordForm, RequestConfirmForm,
                                     UpdateProfileForm)
from questionary.users.utils import (
    save_picture, send_reset_email, send_confirm_email, restricted)
import json
from datetime import datetime as dt
import pdfkit

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
        send_confirm_email(user)
        flash(
            f'חשבון נוצר בעבור {form.username.data}.<br>אנא אשרו את המשתמש באמצעות המייל שקיבלתם לכתובת {form.email.data}.', 'success')
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
            return redirect(next_page) if next_page else redirect(url_for('users.profile', username=user.username))
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


@users.route('/profile/<string:username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    image_file = url_for(
        'static', filename=f'profile_pics/{user.image_file}')
    return render_template('profile.html', user=user, image_file=image_file)


@users.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.gender = form.gender.data
        current_user.show_gender = form.show_gender.data
        current_user.looking_for = form.looking_for.data
        current_user.show_looking = form.show_looking.data
        current_user.about = form.about.data
        current_user.external_link = form.link.data
        db.session.commit()
        return redirect(url_for('users.profile', username=current_user.username))
    elif request.method == 'GET':
        form.gender.data = current_user.gender
        form.show_gender.data = current_user.show_gender
        form.looking_for.data = current_user.looking_for
        form.show_looking.data = current_user.show_looking
        form.about.data = current_user.about
        form.link.data = current_user.external_link
    return render_template('edit_profile.html', form=form)


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(
            f'מייל איפוס סיסמה נשלח ל{form.email.data}. בדקו את המייל שלכם!', 'info')
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
        flash(
            f'מייל אישור חשבון נשלח ל{current_user.email}. בדקו את המייל שלכם!', 'info')
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


@users.route('/user/<string:username>/answer')
def user_results(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not user.categories:
        abort(404)
    categories = Category.query.filter(Category.id.in_(
        user.categories)).order_by(Category.id).all()
    return render_template('answers_jinja.html', categories=categories, user=user, disabled=True)


@users.route('/user/<string:username>/answer/pdf', methods=['GET', 'POST'])
@login_required
def answers_pdf(username):
    # only the owner can download his own pdf
    if username != current_user.username:
        abort(403)
    user = User.query.filter_by(username=username).first_or_404()
    categories = Category.query.filter(Category.id.in_(
        user.categories)).order_by(Category.id).all()
    rendered = render_template(
        'pdf_template.html', categories=categories, user=user, link=url_for('main.home', _external=True))

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
    }
    pdf = pdfkit.from_string(
        rendered,
        False,
        options=options
    )

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=out.pdf'

    return response
