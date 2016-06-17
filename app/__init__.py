from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
mail = Mail()

login_manager = LoginManager()
# session protection to help prevent users' sessions from being stolen
login_manager.session_protection = "basic"
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint)

    from .forum import forum as forum_blueprint
    app.register_blueprint(forum_blueprint)

    from .message import message as message_blueprint
    app.register_blueprint(message_blueprint)

    from .apis import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix= '/apis')

    from .activity import activity as activity_blueprint
    app.register_blueprint(activity_blueprint)

    return app

