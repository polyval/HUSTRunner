# -*- coding: utf-8 -*-
from datetime import datetime
import uuid
import imghdr
import os

from sqlalchemy import or_
from flask import request, redirect, url_for, render_template, flash, current_app, jsonify
from flask_login import current_user, login_required

from . import user
from .forms import EditProfileForm, EditProfileAdiminForm
from .models import User, Role, Follow
from ..forum.models import Post, Comment
from .. import db
from ..decorators import admin_required


@user.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author_id=user.id).all()
    comments = Comment.query.filter_by(author_id=user.id).all()
    activities = posts + comments
    activities = sorted(
        activities, key=lambda activity: activity.date_created, reverse=True)
    # activities = Post.query.join(Comment).filter(or_(Post.author_id == user.id,
    # Comment.author_id == user.id)).order_by('date_created').all()
    return render_template('user/profile.html', user=user, activities=activities)


@user.route('/user/<username>/followees')
@login_required
def followees(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=20, error_out=False
    )
    followees = [{'user': item.followed, 'timestamp': item.timestamp}
                 for item in pagination.items]
    return render_template('followers.html', user=user, title=u'关注的人',
                           endpoint='.followees', pagination=pagination,
                           follows=followees)


@user.route('/user/<username>/followers')
@login_required
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=20, error_out=False
    )
    followers = [{'user': item.follower, 'timestamp': item.timestamp}
                 for item in pagination.items]
    return render_template('followers.html', user=user, title=u'的关注者',
                           endpoint='.followers', pagination=pagination,
                           follows=followers)


@user.route('/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.signature = form.signature.data
        current_user.gender = form.gender.data
        db.session.add(current_user)
        flash(u'个人资料已修改')
        return redirect(url_for('user.profile', username=current_user.username))
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    form.signature.data = current_user.signature
    form.gender.data = current_user.gender
    return render_template('user/edit_profile.html', form=form)


@user.route('/avatar', methods=['POST'])
@login_required
def avatar():
    img = request.files['picture']
    if img:
        dir = os.path.join(current_app.static_folder, 'avatar')

        if not os.path.exists(dir):
            os.makedirs(dir)
        # get unique filename
        while True:
            filename = datetime.now().strftime(
                '%Y%m%d%H%M%S') + uuid.uuid4().hex
            path = "%s/%s" % (dir, filename)
            if not os.path.exists(path):
                break
        try:
            img.save(path)
            # Tests the image data contained in the file named by path
            ext = imghdr.what(path)
            new_path = "%s.%s" % (path, ext)
            os.rename(path, new_path)
        except:
            print "------------------Error: save or open %s" % path

    src = url_for('static', filename='avatar/%s' % os.path.basename(new_path))
    current_user.avatar = src
    db.session.add(current_user)
    db.session.commit()
    return jsonify(src=src)


@user.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdiminForm(user=user)
    if form.validate_on_submit():
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.gender = form.gender.data
        user.signature = form.signature.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'用户资料已修改')
        return redirect(url_for('user.profile', username=user.username))
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.gender.data = user.gender
    form.signature.data = user.signature
    form.about_me.data = user.about_me
    return render_template('user/edit_profile.html', form=form, user=user)


@user.route('/user/<username>/posts')
def posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.date_created.desc()).all()
    return render_template('user/posts.html', user=user, posts=posts)


@user.route('/user/<username>/comments')
def comments(username):
    user = User.query.filter_by(username=username).first_or_404()
    comments = Comment.query.filter_by(author_id=user.id).order_by(
        Comment.date_created.desc()).all()
    return render_template('user/comments.html', user=user, comments=comments)


@user.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('user/security_setting.html', user=current_user)


@user.route('/settings/notification', methods=['GET', 'POST'])
@login_required
def notification():
    # TODO
    return render_template('user/notify_setting.html')
