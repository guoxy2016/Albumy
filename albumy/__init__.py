import os

import click
from flask import Flask, render_template
from flask_login import current_user

from .blueprints.ajax import ajax_bp
from .blueprints.auth import auth_bp
from .blueprints.main import main_bp
from .blueprints.user import user_bp
from .extensions import db, mail, login_manager, bootstrap, migrate, moment, dropzone, csrf, avatars
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
    pass


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


def register_blueprints(app=None):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(ajax_bp, url_prefix='/ajax')


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
        return render_template('errors/400.html', description=e.description), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html', description=e.description), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html', description=e.description), 404

    @app.errorhandler(413)
    def too_large(e):
        return render_template('errors/413.html', description=e.description), 413

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html', description=e.description), 500


def register_commends(app=None):
    @app.cli.command(name='init_db')
    @click.option('--drop', is_flag=True, help='Drop all data before create.')
    def init_db(drop):
        """Initialize the database"""
        if drop:
            click.confirm('All data well be deleted, are you sure?', abort=True)
            db.drop_all()
            click.echo('drop done!')
        db.create_all()
        click.echo('create all.')

    @app.cli.command(name='init')
    def init():
        """Initialize Albumy"""
        click.echo('Initializing the database')
        db.create_all()

        click.echo('Initializing the roles and permissions')
        Role.init_role()

        click.echo('Done!')

    @app.cli.command()
    @click.option('--user', default=6, help='Quantity of users, default is 6')
    @click.option('--photo', default=30, help='Quantity of photo, default is 30')
    @click.option('--tag', default=20, help='quality of tag, default is 20')
    @click.option('--comment', default=100, help='Quality of comment, default is 100')
    @click.option('--collect', default=50, help='Quality of collect, default is 50')
    def forge(user, photo, tag, comment, collect):
        """Generate fake data"""
        from .fakes import fake_admin, fake_users, fake_tags, fake_photos, fake_comments, fake_collects

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

        click.echo('Done!')
