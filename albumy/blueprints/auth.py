from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import current_user, login_required, login_user, logout_user, login_fresh, confirm_login

from ..emails import send_confirm_email, send_reset_password_email
from ..extensions import db
from ..forms.auth import RegisterForm, LoginForm, ForgetPasswordForm, ResetPasswordForm, ReLoginForm
from ..models import User
from ..settings import Operations
from ..utils import generate_token, validate_token, redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    next_path = request.args.get('next')
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        user = User(name=name, email=email, username=username)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()

        token = generate_token(user=user, operation=Operations.CONFIRM)
        send_confirm_email(user, token)

        flash('验证邮件已发送, 请注意查收.', 'info')
        if next_path:
            return redirect(url_for('.login', next=next_path))
        return redirect(url_for('.login'))
    return render_template('auth/register.jinja2', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user is not None and user.validate_password(password):
            if login_user(user, remember=form.remember.data):
                flash('欢迎回来!', 'success')
                return redirect_back()
            else:
                flash('帐户被封禁了', 'warning')
                return redirect(url_for('main.index'))
        flash('用户名或密码错误', 'warning')
    return render_template('auth/login.jinja2', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出成功', 'success')
    return redirect_back()


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    operation = Operations.CONFIRM
    if validate_token(token, current_user, operation):
        flash('您的账户以验证', 'success')
        return redirect(url_for('main.index'))
    else:
        flash('您的验证信息已过期', 'danger')
        return redirect(url_for('.resend_confirm_email'))


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    token = generate_token(current_user, Operations.CONFIRM)
    send_confirm_email(current_user, token)
    flash('验证邮件已发送', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_token(user, Operations.RESET_PASSWORD)
            send_reset_password_email(user, token)
            flash('邮件已发送请注意查收', 'info')
            return redirect(url_for('.login'))
        flash('邮件验证错误!', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('auth/reset_password.jinja2', form=form)


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('邮箱验证失败', 'danger')
            return redirect(url_for('.forget_password'))
        if validate_token(token, user, Operations.RESET_PASSWORD, password=password):
            flash('修改密码成功', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('令牌失效, 重新发送验证邮件', 'danger')
            return redirect(url_for('.forget_password'))

    return render_template('auth/reset_password.jinja2', form=form)


@auth_bp.route('re-authenticate', methods=['GET', 'POST'])
@login_required
def re_authenticate():
    if login_fresh():
        return redirect(url_for('main.index'))
    form = ReLoginForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.password.data):
            confirm_login()
            return redirect_back()
        flash('密码错误, 请重新输入', 'warning')
    return render_template('auth/login.jinja2', form=form)
