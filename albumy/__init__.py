import os

import click
from flask import Flask, render_template

from .blueprints.auth import auth_bp
from .blueprints.main import main_bp
from .blueprints.user import user_bp
from .extensions import db, mail, login_manager, bootstrap, migrate, moment, dropzone, csrf, avatars
from .models import User, Role, Permission


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
    ...


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


def register_shell_context(app=None):
    @app.shell_context_processor
    def template_context():
        return dict(db=db, User=User, Role=Role, Permission=Permission)


def register_template_context(app=None):
    ...


def register_errors(app=None):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html')

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html')

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html')

    @app.errorhandler(413)
    def too_large(e):
        return render_template('errors/413.html')

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html')


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
    @click.option('--user', default=10, help='Quantity of users, default is 10')
    def forge(user):
        """Generate fake data"""
        from .fakes import fake_admin, fake_users

        db.drop_all()
        db.create_all()

        click.echo('Initializing the roles and permissions')
        Role.init_role()

        click.echo('Generating Administrator...')
        fake_admin()

        click.echo('Generating %d users...' % user)
        fake_users(count=user)

        click.echo('Done!')
