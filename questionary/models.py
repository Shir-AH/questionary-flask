from questionary import db, login_manager, admin, AppModelView
from datetime import datetime as dt
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpeg')
    password = db.Column(db.String(60), nullable=False)
    answers = db.relationship('Answer', backref='author', lazy=True)
    categories = db.Column(db.ARRAY(db.Integer()))
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime)
    external_link = db.Column(db.String(120))
    gender = db.Column(db.String(60))
    show_gender = db.Column(db.Boolean, default=False)
    looking_for = db.Column(db.String(60))
    show_looking = db.Column(db.Boolean, default=False)
    about = db.Column(db.Text)

    def __repr__(self):
        return f"User '{self.username}', '{self.email}'"

    def get_reset_token(self, expires_seconds=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_confirmation_token(self, expires_seconds=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_seconds)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    @property
    def has_results(self):
        return 0 < len(Answer.query.filter_by(author=self).all())

    @property
    def is_confirmed(self):
        return self.confirmed

    def answer(self, question_id):
        question = Questions.query.filter_by(id=question_id).first()
        return Answer.query.filter_by(author=self, question=question) \
            .order_by(Answer.date_posted.desc()).first()


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    explanation = db.Column(db.Text)
    questions = db.relationship('Questions', backref='category', lazy=True)

    @property
    def explanation_size(self):
        length = len(self.explanation)
        if length < 20:
            return 'small'
        if length < 40:
            return 'medium'
        if length < 100:
            return 'large'
        return 'xlarge'


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    category_name = db.Column(db.String, db.ForeignKey('category.name'))
    answers = db.relationship('Answer', backref='question', lazy=True)

    @property
    def explanation_size(self):
        length = len(self.explanation)
        if length < 20:
            return 'small'
        if length < 40:
            return 'medium'
        if length < 100:
            return 'large'
        return 'xlarge'


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(
        'questions.id'), nullable=False)
    exp_answer = db.Column(db.Integer, nullable=False, default=0)
    wil_answer = db.Column(db.Integer, nullable=False, default=0)


class SiteData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String, nullable=True, unique=True)
    value = db.Column(db.Text, nullable=True)

    @classmethod
    def data_dict(cls):
        site_data = cls.query.all()
        site_data_dict = {}
        for site_data_obj in site_data:
            site_data_dict[site_data_obj.reference] = site_data_obj.value
        return site_data_dict


class UserView(AppModelView):
    form_columns = ['id', 'username', 'email', 'confirmed',
                    'confirmed_on', 'external_link', 'gender', 'looking_for', 'about']


admin.add_view(UserView(User, db.session))
admin.add_view(AppModelView(Category, db.session))
admin.add_view(AppModelView(Questions, db.session))
admin.add_view(AppModelView(SiteData, db.session))
