# -*- coding: utf-8 -*-
from flask import request, redirect, url_for, render_template, flash
from flask_login import current_user, login_required

from . import user
from .forms import EditProfileForm, EditProfileAdiminForm
from .models import User, Role, Follow
from ..forum.models import Post
from .. import db
from ..decorators import admin_required


@user.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.date_created.desc()).all()
    return render_template('user/profile.html', user=user, posts=posts)


@user.route('/user/<username>/followees')
def followees(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=20, error_out=False
    )
    followees = [{'user': item.followed, 'timestamp': item.timestamp}
                 for item in pagination.items]
    return render_template('followers.html', user=user, title=u'关注的人',
                           endpoint='.followees',pagination=pagination,
                           follows=followees)


@user.route('/user/<username>/followers')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=20, error_out=False
    )
    followers = [{'user': item.follower, 'timestamp': item.timestamp}
                 for item in pagination.items]
    return render_template('followers.html', user=user, title=u'的关注者',
                           endpoint='.followers',pagination=pagination,
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


@user.route('/settings/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('user/security_setting.html', user=current_user)
