# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, jsonify

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


@forum.route('/post/<slug>/comment', methods=['GET', 'POST'])
def add_comment(slug):
    if request.method == 'POST':
        content = request.json['content']
        parent_id = request.json['parent_id']
        if parent_id:
            comment = Comment(content_html=content,
                              author=current_user._get_current_object(),
                              parent=Comment.query.get(parent_id))
        else:
            comment = Comment(content_html=content,
                              author=current_user._get_current_object(),
                              post=Post.query.filter_by(slug=slug).first())
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment_id = comment.id, timestamp = comment.date_created)