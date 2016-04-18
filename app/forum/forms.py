# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length


class PostForm(Form):
    title = StringField(u'标题', validators=[DataRequired(), Length(1, 150)])
    topic = SelectField(u'主题', validators=[DataRequired()],
                        choices=[(u'约跑', u'约跑步'),
                                 (u'技术交流', u'技术交流'),
                                 (u'赛事活动', u'赛事活动'),
                                 (u'灌水', u'灌水')])
