# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError, regexp
from ..user.models import User

USERNAME_RE = r'^[\u4e00-\u9fa5_A-Za-z][\u4e00-\u9fa5_a-zA-Z0-9.]+$'
is_username = regexp(USERNAME_RE,
                     message=u"用户名由中文，字母，数字，点或下划线组成，且首字母只能是中文或字母")


class LoginForm(Form):
    login = StringField(u"帐号", validators=[
        DataRequired(message=u"请填写用户名或邮箱")]
                        )

    password = PasswordField(u"密码", validators=[
        DataRequired(message=u"请输入密码")])

    remember_me = BooleanField(u"保持登录", default=False)

    submit = SubmitField(u"登录")


class RegistrationForm(Form):
    username = StringField(u"用户名", validators=[DataRequired(message=""), is_username])
    email = StringField(u"邮箱", validators=[DataRequired(message=""), Email()])
    password = PasswordField(u"密码", validators=[DataRequired(message=""),
                                                     EqualTo("password2", message="")])
    password2 = PasswordField(u"重复密码", validators=[DataRequired(message="")])
    submit = SubmitField(u"注册")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u"用户名已存在")

    def validate_email(self, field):
        if User.qury.filter_by(email=field.data).first():
            raise ValidationError(u"邮箱已注册")


class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[DataRequired()])
    new_password = PasswordField(u'新密码', validators=[DataRequired(),
                                                     EqualTo("new_password2", message=u'密码不一致')])
    new_password2 = PasswordField(u'重复新密码', validators=[DataRequired()])
    submit = SubmitField(u'更改密码')


class PasswordResetRequestForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField(u'重置密码')


class PasswordResetForm(Form):
    email = StringField(u'邮箱', validators=[DataRequired(), Email()])
    password = PasswordField(u'新密码', validators=[DataRequired(),
                                                     EqualTo("password2", message=u'密码不一致')])
    password2 = PasswordField(u'重复新密码', validators=[DataRequired()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'邮箱不正确')


class ChangeEmailForm(Form):
    email = StringField(u'新邮箱', validators=[DataRequired(), Email()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u'更改邮箱')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已注册')

