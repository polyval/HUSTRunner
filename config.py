import os
import platform

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "it's really hard to guess"
    # Commit database changes when tearing down
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[HUSTRunner]'
    FLASKY_MAIL_SENDER = 'HUSTRunner Admin <HUSTRunner@example.com>'
    FLASK_ADMIN = 'polyval@mail.com'

    @staticmethod
    def init__app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:password@localhost/hustrunner'

    @classmethod
    def init_app(cls, app):
        Config.init__app(app)

        import logging
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler('hustrunner.log', maxBytes=1024*1024*100, backupCount=20)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    if platform.system() == 'Windows':
        SQLALCHEMY_DATABASE_URI = \
            'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    else:
        SQLALCHEMY_DATABASE_URI = \
            'sqlite:////' + os.path.join(basedir, 'data-test.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init__app(app)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
}
