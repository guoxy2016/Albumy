from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, PasswordField
from wtforms.validators import DataRequired, Optional, Length, ValidationError, Regexp, InputRequired, EqualTo, Email

from ..models import User


class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[DataRequired('请输入姓名'), Length(1, 30)])
    username = StringField('用户名', validators=[
        DataRequired('请输入用户名'), Length(1, 20),
        Regexp(r'^[a-zA-Z0-9]*$', message='用户名只能包含a-z, A-Z, 0-9之内的字符')
    ])
    website = StringField('个人网址', validators=[Optional(), Length(0, 254)])
    location = StringField('城市', validators=[Optional(), Length(0, 50)])
    bio = TextAreaField('个人经历', validators=[Optional(), Length(0, 120)])
    submit = SubmitField('提交')

    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被使用')


class UploadAvatarForm(FlaskForm):
    image = FileField('上传头像(< 5MB)', validators=[
        FileRequired(),
        FileAllowed({'jpg', 'png', 'jpeg'}, '只能上传.jpg或.png文件')
    ])
    submit = SubmitField('上传')


class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('裁减并保存')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[InputRequired('请输入密码')])
    password1 = PasswordField('新密码', validators=[InputRequired(), Length(8, 128), EqualTo('password2', '两次输入的密码不一致')])
    password2 = PasswordField('确认密码', validators=[InputRequired()])
    submit = SubmitField('修改')


class ChangeEmailForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired('请输入内容'), Email('Email格式错误'), Length(1, 254, 'Email的长度超过254')
    ])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first() is not None:
            raise ValidationError('Email已被注册, 请换一个试试.')
