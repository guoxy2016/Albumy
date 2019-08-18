import logging
import os
from logging.handlers import RotatingFileHandler, SMTPHandler

import click
from flask import Flask, render_template, request, jsonify
from flask_login import current_user

from .blueprints.admin import admin_bp
from .blueprints.ajax import ajax_bp
from .blueprints.auth import auth_bp
from .blueprints.main import main_bp
from .blueprints.user import user_bp
from .extensions import db, mail, login_manager, bootstrap, migrate, moment, dropzone, csrf, avatars, toolbar, whooshee
from .models import User, Role, Permission, Photo, Tag, Comment, Collect, Follow, Notification


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('albumy')
    from albumy.settings import configs
    app.config.from_object(configs[config_name])

    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_template_context(app)
    register_errors(app)
    register_commends(app)

    return app


def register_logging(app=None):
    app.logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - "%(pathname)s", line:%(lineno)s - %(message)s')
    file_handler = RotatingFileHandler('logs/data.log', maxBytes=10 * 1024 * 1024, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    class RequestFormatter(logging.Formatter):
        def format(self, record):
            record.url = request.url
            record.remote_addr = request.remote_addr
            return super(RequestFormatter, self).format(record)

    request_formatter = RequestFormatter(
        '[%(asctime)s] - "%(remote_addr)s : %(url)s" - %(levelname)s - "%(pathname)s", line:%(lineno)s - %(message)s'
    )

    mail_handler = SMTPHandler(
        mailhost=app.config['MAIL_SERVER'],
        fromaddr=app.config['MAIL_USERNAME'],
        toaddrs=app.config['ALBUMY_ADMIN_EMAIL'],
        subject='Albumy程序错误',
        credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
    )
    mail_handler.setFormatter(request_formatter)
    mail_handler.setLevel(logging.ERROR)

    if not app.debug:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(mail_handler)


def register_extensions(app=None):
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    dropzone.init_app(app)
    csrf.init_app(app)
    avatars.init_app(app)
    toolbar.init_app(app)
    whooshee.init_app(app)


def register_blueprints(app=None):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(ajax_bp, url_prefix='/ajax')
    app.register_blueprint(admin_bp, url_prefix='/admin')


def register_shell_context(app=None):
    @app.shell_context_processor
    def shell_context():
        return dict(db=db, User=User, Role=Role, Permission=Permission, Photo=Photo, Tag=Tag, Comment=Comment,
                    Collect=Collect, Follow=Follow)


def register_template_context(app=None):
    @app.context_processor
    def make_template_context():
        if current_user.is_authenticated:
            notification_count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
        else:
            notification_count = None
        return dict(notification_count=notification_count)


def register_errors(app=None):
    @app.errorhandler(400)
    def bad_request(e):
        if request.path.startswith('/ajax'):
            return jsonify(message=e.description), 400
        return render_template('errors/error.jinja2', code=e.code, name=e.name, description=e.description), 400

    @app.errorhandler(403)
    def forbidden(e):
        if request.path.startswith('/ajax'):
            return jsonify(message=e.description), 403
        return render_template('errors/error.jinja2', code=e.code, name=e.name, description=e.description), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/ajax'):
            return jsonify(message=e.description), 404
        return render_template('errors/error.jinja2', code=e.code, name=e.name, description=e.description), 404

    @app.errorhandler(405)
    def not_found(e):
        if request.path.startswith('/ajax'):
            return jsonify(message=e.description), 405
        return render_template('errors/error.jinja2', code=e.code, name=e.name, description=e.description), 405

    @app.errorhandler(413)
    def too_large(e):
        if request.path.startswith('/ajax'):
            return jsonify(message=e.description), 413
        return render_template('errors/error.jinja2', code=e.code, name=e.name, description=e.description), 413

    @app.errorhandler(500)
    def server_error(_):
        description = (
            "The server encountered an internal error and was unable to"
            " complete your request. Either the server is overloaded or"
            " there is an error in the application."
        )
        if request.path.startswith('/ajax'):
            return jsonify(message=description), 500

        return render_template('errors/500.jinja2', description=description), 500


def register_commends(app=None):
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Drop all data before create.')
    def init_db(drop):
        """Initialize the database"""
        if drop:
            click.confirm('All data well be deleted, are you sure?', abort=True)
            db.drop_all()
            click.echo('drop done!')
        db.create_all()
        click.echo('create all.')

    @app.cli.command()
    def init():
        """Initialize Albumy"""
        click.echo('Initializing the database')
        db.create_all()

        click.echo('Initializing the roles and permissions')
        Role.init_role()

        click.echo('Done!')

    @app.cli.command()
    @click.option('-e', '--email', prompt=True, help='输入邮箱, 登陆使用')
    @click.password_option('-p', '--password', prompt=True, help='输入密码, 长度8-128位')
    @click.option('-n', '--name', help='姓名, 指定之后可以创建头像')
    @click.option('-u', '--username', help='用户名, 指定唯一用户标识')
    def create_superuser(email, password, name, username):
        """建超级管理用户如果用户已经存在就把该用户变为超级用户"""
        from .utils import validate_email
        role = Role.query.filter_by(name='Administrator').first()
        if not role:
            click.echo('请先执行 flask init')
            raise click.Abort()
        if not validate_email(email):
            raise click.BadArgumentUsage('邮箱的格式不正确!')
        if 8 > len(password) or len(password) > 128:
            raise click.BadArgumentUsage('密码的长度范围是8-128')
        user = User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()
        if user is None:
            user = User(email=email, name=name or email, username=username or name or email)
            click.echo('正在创建超级用户')
        else:
            click.echo('更改用户:\n'
                       '    Name: %s\n'
                       '    Email: %s\n'
                       '    Username: %s\n'
                       '为超级管理员' % (user.name, user.email, user.username))
        user.confirmed = True
        user.password = password
        user.role = role
        db.session.add(user)
        db.session.commit()
        click.echo('完成!')

    @app.cli.command()
    @click.option('--user', default=6, help='Quantity of users, default is 6')
    @click.option('--photo', default=30, help='Quantity of photo, default is 30')
    @click.option('--tag', default=20, help='Quality of tag, default is 20')
    @click.option('--comment', default=100, help='Quality of comment, default is 100')
    @click.option('--collect', default=50, help='Quality of collect, default is 50')
    @click.option('--follow', default=20, help='Quality of follow, default is 20')
    def forge(user, photo, tag, comment, collect, follow):
        """Generate fake data"""
        from .fakes import fake_admin, fake_users, fake_tags, fake_photos, fake_comments, fake_collects, fake_follow

        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions')
        Role.init_role()

        click.echo('Generating Administrator...')
        fake_admin()

        click.echo('Generating %d users...' % user)
        fake_users(count=user)

        click.echo('Generating %d tags...' % tag)
        fake_tags(count=tag)

        click.echo('Generating %d photos...' % photo)
        fake_photos(count=photo)

        click.echo('Generating %d comments...' % comment)
        fake_comments(count=comment)

        click.echo('Generating %d collects...' % collect)
        fake_collects(count=collect)

        click.echo('Generating %d follows...' % follow)
        fake_follow(count=follow)

        click.echo('Done!')
