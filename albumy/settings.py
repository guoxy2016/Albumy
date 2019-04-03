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
    ALBUMY_UPLOAD_PATH = os.path.join(basedir, 'uploads')
    ALBUMY_ALLOW_EXTENSIONS = ['jpg', 'jpeg', 'png', ]
    ALBUMY_PHOTO_SIZE = {
        'small': 400,
        'medium': 800,
    }
    ALBUMY_PHOTO_SUFFIX = {
        ALBUMY_PHOTO_SIZE['small']: '_s',
        ALBUMY_PHOTO_SIZE['medium']: '_m',
    }

    SECRET_KEY = 'secret key'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Albumy', MAIL_USERNAME)

    DROPZONE_MAX_FILE_SIZE = 5
    DROPZONE_MAX_FILES = 20
    DROPZONE_DEFAULT_MESSAGE = '<h2>拖拽文件到这里,或点击上传</h2>'
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = '.png, .jpg, .jpeg, .jpe, .tif'
    DROPZONE_INVALID_FILE_TYPE = '不支持的文件格式'
    DROPZONE_FILE_TOO_BIG = '当前文件过大{{filesize}}MB.最大支持{{maxFilesize}}MB的文件'
    DROPZONE_SERVER_ERROR = '服务端错误:{{statusCode}}'
    DROPZONE_BROWSER_UNSUPPORTED = '浏览器不支持'
    DROPZONE_MAX_FILE_EXCEED = '超出最大上传数量'
    DROPZONE_ENABLE_CSRF = True

    AVATARS_SAVE_PATH = os.path.join(ALBUMY_UPLOAD_PATH, 'avatars')
    AVATARS_SIZE_TUPLE = (30, 100, 200)


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
