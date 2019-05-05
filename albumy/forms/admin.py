from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

from .user import EditProfileForm
from ..models import Role, User


class EditProfileAdminForm(EditProfileForm):
    email = StringField('Email', validators=[
        DataRequired('请输入内容, 不能以空格开头'),
        Email('邮件格式错误'),
        Length(1, 254, '不支持超过254个字符的Email地址')
    ])
    role = SelectField('权限', coerce=int)
    active = BooleanField('激活')
    confirmed = BooleanField('认证')
    submit = SubmitField('保存')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all() if
                             role.name != 'Administrator']
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first() is not None:
            raise ValidationError('用户名已被占用')

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('Email已被占用')

