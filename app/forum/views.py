# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import current_user, login_required

from .. import db
from . import forum
from .models import Post, Topic, Comment
from ..user.models import Permission
from ..message.models import Notification
from .forms import PostForm


@forum.route('/edit/<slug>', methods=['GET', 'POST'])
@forum.route('/new_post', methods=['GET', 'POST'])
@login_required
def new_post(slug=None):
    form = PostForm()
    if slug:
        post = Post.query.filter_by(slug=slug).first()
        if post.author_id != current_user.id:
            abort(404)
        if form.validate_on_submit():
            post.content_html = request.form['editorValue']
            post.topic = Topic.query.filter_by(title=form.topic.data).first()
            post.title = form.title.data
            db.session.add(post)
            flash(u'文章已修改')
            return redirect(url_for('main.index'))
        form.title.default = post.title
        form.topic.default = post.topic
        form.process()
        return render_template('new_post.html', form=form, post=post)
    else:
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
    if request.method == 'POST':
        # Post.query.filter_by(slug=slug).delete() may not
        # delete its comments. See stackoverflow:
        # questions/5033547/sqlachemy-cascade-delete#answer-12801654
        p = Post.query.filter_by(slug=slug).first()
        if p.author == current_user or current_user.can(Permission.MODERATE_POSTS):
            db.session.delete(p)
        else:
            abort(404)
        return redirect(url_for('main.index'))
    post = Post.query.filter_by(slug=slug).first_or_404()
    comments = Comment.query.filter(
        Comment.post_id == post.id, Comment.parent == None).all()
    post.views += 1
    db.session.add(post)
    return render_template('article.html', post=post, comments=comments)


@forum.route('/post/<slug>/comment', methods=['GET', 'POST'])
@login_required
def add_comment(slug):
    if request.method == 'POST':
        content = request.json['content']
        # id of parent comment
        parent_id = request.json['parent_id']
        if parent_id:
            comment = Comment(content_html=content,
                              author=current_user._get_current_object(),
                              parent=Comment.query.get(parent_id),
                              post=Post.query.filter_by(slug=slug).first())
        else:
            comment = Comment(content_html=content,
                              author=current_user._get_current_object(),
                              post=Post.query.filter_by(slug=slug).first())
        db.session.add(comment)
        db.session.commit()
        if parent_id:
            receive_id = Comment.query.get(parent_id).author.id
        else:
            receive_id = Post.query.filter_by(slug=slug).first().author.id
        notify = Notification(sender_id=current_user.id,
                              receive_id=receive_id,
                              target=comment.id,
                              target_type='comment',
                              action='comment')
        db.session.add(notify)
        return jsonify(comment_id=comment.id, timestamp=comment.date_created)
