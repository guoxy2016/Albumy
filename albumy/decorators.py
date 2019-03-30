from functools import wraps

from flask import Markup, url_for, flash, redirect
from flask_login import current_user


def confirm_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            message = Markup('请先验证您的邮件, '
                             '如果没有收到验证邮件可以'
                             '<a class="alert-link" href="%s">点击这里</a>重新发送'
                             % url_for('auth.resend_confirm_email'))
            flash(message, 'warning')
            return redirect('main.index')
        return func(*args, **kwargs)
    return decorated_function

