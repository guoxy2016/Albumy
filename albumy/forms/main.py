from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField
from wtforms.validators import Optional, Length, DataRequired


class DescriptionForm(FlaskForm):
    description = TextAreaField('简介', validators=[Optional(), Length(0, 500, '最长500个字')])
    submit = SubmitField('保存')


class TagForm(FlaskForm):
    tag = StringField('添加标签(使用空格进行分割)', validators=[Optional(), Length(0, 64, '最长64个字')])
    submit = SubmitField('保存')


class CommentForm(FlaskForm):
    body = TextAreaField('', validators=[DataRequired('请输入评论')])
    submit = SubmitField('提交')
