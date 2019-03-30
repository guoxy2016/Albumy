from threading import Thread

from flask import current_app, render_template
from flask_mail import Message

from .extensions import mail


def send_email(subject, to, template, **kwargs):
    message = Message(current_app.config['ALBUMY_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.html = render_template(template + '.html', **kwargs)
    message.body = render_template(template + '.txt', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_email, args=(app, message))
    thr.start()
    return thr


def _send_async_email(app, message):
    with app.app_context():
        mail.send(message)


def send_confirm_email(user, token, to=None):
    send_email('验证邮箱', to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token, to=None):
    send_email('重置密码', to or user.email, template='emails/reset_password', user=user, token=token)
