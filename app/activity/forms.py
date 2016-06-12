# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Optional


class ActivityForm(Form):
    title = StringField(u'活动名称', validators=[DataRequired(), Length(1,100)])
    brief = TextAreaField(u'活动简介', validators=[DataRequired(), Length(1,500)])
    date_expired = IntegerField(u'到期时间', validators=[Optional()])
    submit = SubmitField(u'确定')