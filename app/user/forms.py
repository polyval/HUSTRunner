# -*- coding: utf-8 -*-
from flask_wtf import Form
from flask_login import current_user
from wtforms import StringField, BooleanField, SubmitField, SelectField, TextAreaField, RadioField
from wtforms.validators import DataRequired, Length, ValidationError, regexp, Optional

from .models import User, Role

USERNAME_RE = r'^[\u4e00-\u9fa5_A-Za-z][\u4e00-\u9fa5_a-zA-Z0-9.]+$'
is_username = regexp(USERNAME_RE,
                     message=u"用户名由中文，字母，数字，点或下划线组成，且首字母只能是中文或字母")


class EditProfileForm(Form):
    username = StringField(u'用户名', validators=[DataRequired(message=""), Length(1, 64), is_username])
    gender = SelectField(u'性别', validators=[Optional()], choices=[('', ''), (u'男', u'男'), (u'女', u'女')])
    signature = StringField(u'个性签名', validators=[Length(1, 100)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')

    # TODO: There should have an interval of changing username
    def validate_username(self, field):
        if field.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class EditProfileAdiminForm(Form):
    """The form is used for management"""
    username = StringField(u"用户名", validators=[DataRequired(message=""), Length(1, 64), is_username])
    confirmed = BooleanField(u'邮箱验证')
    role = SelectField(u'角色', coerce=int)
    gender = SelectField(u'性别', validators=[Optional()], choices=[('', ''), (u'男', u'男'), (u'女', u'女')])
    signature = StringField(u'个性签名', validators=[Length(1, 100)])
    about_me = TextAreaField(u'个人简介')
    submit = SubmitField(u'提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdiminForm, self).__init__(*args, **kwargs)
        # choices is what SelectField needed to render select field
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')


class NotifyForm(Form):
    pm_all = RadioField(u'私信', choices=[(True, u'接收所有人私信'), (False, u'只接收我关注的人的私信')])
    be_followed = RadioField(u'有人关注了我', choices=[(True, u'接收'), (False, u'不接收')])
    post_be_voted = RadioField(u'赞了我的文章',
                               choices=[(0, u'接收所有人的消息'), (1, u'只接收关注人的消息'), (2, u'不接收')])
    comment_be_voted = RadioField(u'赞了我的评论',
                                  choices=[(0, u'接收所有人的消息'), (1, u'只接收关注人的消息'), (2, u'不接收')])
    comment = RadioField(u'评论我',
                         choices=[(0, u'接收所有人的消息'), (1, u'只接收关注人的消息'), (2, u'不接收')])
