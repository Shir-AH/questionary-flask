from questionary import db, login_manager
from datetime import datetime as dt
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def add_column(app, table_name, column):
    engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    engine.execute(
        f'ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='default.jpeg')
    password = db.Column(db.String(60), nullable=False)
    results = db.relationship('QuestionaryResults',
                              backref='author', lazy=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

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
        return 0 < len(QuestionaryResults.query.filter_by(author=self).all())

    @property
    def is_confirmed(self):
        return self.confirmed


class QuestionaryResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    questionary_results = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Results(result #{self.id}: '{self.date_posted}')"


class Category(db.Model):
    name = db.Column(db.String(120), primary_key=True, nullable=False)
    questions = db.relationship('Questions', backref='category', lazy=True)


class Questions(db.Model):
    question = db.Column(db.Text, primary_key=True, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    category_name = db.Column(db.String, db.ForeignKey('category.name'))
