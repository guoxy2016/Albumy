import os
from base64 import b64encode

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BaseConfig:
    ALBUMY_ADMIN_EMAIL = os.getenv('ALBUMY_ADMIN', 'admin@helloflask.com')
    ALBUMY_PHOTO_PER_PAGE = 12
    ALBUMY_COMMENT_PER_PAGE = 15
    ALBUMY_NOTIFICATION_PER_PAGE = 20
    ALBUMY_USER_PER_PAGE = 20
    ALBUMY_MANAGE_PHOTO_PER_PAGE = 20
    ALBUMY_MANAGE_USER_PER_PAGE = 30
    ALBUMY_MANAGE_TAG_PER_PAGE = 50
    ALBUMY_MANAGE_COMMENT_PER_PAGE = 30
    ALBUMY_SEARCH_RESULT_PER_PAGE = 20
    ALBUMY_MAIL_SUBJECT_PREFIX = '[Albumy]'

    SECRET_KEY = 'secret key'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Albumy', MAIL_USERNAME)


class Development(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite3')


class Testing(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLE = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class Production(BaseConfig):
    SECRET_KEY = os.getenv('SECRET_KEY') or b64encode(os.urandom(32)).decode()
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite3')


configs = {
    'development': Development,
    'testing': Testing,
    'production': Production
}


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'
