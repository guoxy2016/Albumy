from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError, Regexp

from albumy.models import User


class RegisterForm(FlaskForm):
    name = StringField('姓名', validators=[
        DataRequired(),
        Length(1, 30, '姓名的长度不超过30个字')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(1, 254, '不支持超过254个字符的Email地址')
    ])
    username = StringField('用户名', validators=[
        DataRequired(),
        Regexp('^[A-Za-z0-9_]*$', message='用户名中只能包含大小写字母, 数字, 以及下划线.'),
        Length(1, 20, '过长')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(),
        Length(8, 128, '密码的长度在8-128位之间')
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', '两次输入的密码不一致'),
        Length(8, 128, '密码的长度在8-128位之间')
    ])
    submit = SubmitField('提交')

    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('这个Email已被注册!')

    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('这个用户名已被注册!')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254, 'Email的长度超过254'), Email('Email邮件格式错误')])
    password = PasswordField('密码', validators=[DataRequired(), Length(8, 128, '密码的长度在8-128位之间')])
    remember = BooleanField('记住我')
    submit = SubmitField('登陆')


class ForgetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254, 'Email的长度超过254'), Email('错误的email地址')])
    submit = SubmitField('发送')


class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 254, 'Email的长度超过254'), Email('错误的email地址')])
    password = PasswordField('密码', validators=[DataRequired(), Length(8, 128, '密码的长度在8-128位之间')])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(),
        EqualTo('password', '两次输入的密码不一致'),
        Length(8, 128, '密码的长度在8-128位之间')
    ])
    submit = SubmitField('保存')
