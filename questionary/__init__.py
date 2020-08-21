from flask import Flask, redirect, url_for, abort
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from questionary.config import Config
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'העמוד הזה זמין רק למי שנרשם לאתר - בבקשה היכנסו לחשבון שלכם כדי לראות אותו.'
mail = Mail()
migrate = Migrate()
admin = Admin()


class AppIndexView(AdminIndexView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.email in ['matan.arielhavron1@gmail.com']:
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return abort(404)


class AppModelView(ModelView):
    def is_accessible(self):
        if current_user.is_authenticated:
            if current_user.email in ['matan.arielhavron1@gmail.com']:
                return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        return abort(404)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    admin.init_app(app, index_view=AppIndexView())

    from questionary.main.routes import main
    from questionary.users.routes import users
    from questionary.errors.handlers import errors
    # from questionary.google.routes import google
    # from questionary._admin_tools.routes import admin_tools

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(errors)
    # app.register_blueprint(google)
    # app.register_blueprint(admin_tools)

    return app
