# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash

from flask_login import current_user, login_required

from .. import db
from . import forum
from .models import Post, Topic, Comment
from .forms import PostForm


@forum.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        content = request.form['editorValue']
        topic = Topic.query.filter_by(title=form.topic.data).first()
        author = current_user._get_current_object()
        title = form.title.data
        post = Post(content_html=content,
                    topic=topic,
                    author=author,
                    title=title)
        post.slug = post.slugify()
        db.session.add(post)
        db.session.commit()
        flash(u'文章已发布')
        return redirect(url_for('main.index'))
    return render_template('new_post.html', form=form)


@forum.route('/post/<slug>', methods=['GET', 'POST'])
def view_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    comments = Comment.query.filter_by(post_id=post.id).all()
    post.views += 1
    db.session.add(post)
    return render_template('article.html', post=post, comments=comments)
