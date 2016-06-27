from flask import request, jsonify, render_template, redirect, url_for, abort
from flask_login import login_required, current_user

from .. import db
from . import activity
from .models import Activity, ActivityQuestion
from .forms import ActivityForm


@activity.route('/activities')
def view_all():
    page = request.args.get('page', 1, type=int)
    pagination = Activity.query.order_by(Activity.date_expired.desc()).paginate(page=page, per_page=20, error_out=False)
    activities = pagination.items
    return render_template('activities.html', activities=activities, pagination=pagination)


@activity.route('/activity', methods=['POST'])
@login_required
def join_activity():
    action = request.form.get('action')
    activity_id = request.form.get('activity_id', type=int)
    user = current_user._get_current_object()
    a = Activity.query.get(activity_id)
    a.participants.append(user) if action == 'join' else a.participants.remove(user)
    db.session.add(a)
    return jsonify(msg=action + 'success')


@activity.route('/activity/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def view_activity(id):
    activity = Activity.query.get(id)
    if request.method == 'POST':
        from ..message.models import Notification
        to_id = request.form.get('to_id', type=int)
        q = ActivityQuestion(author_id=current_user.id,
                             to_id=to_id,
                             content=request.form.get('content'),
                             activity_id=id)
        db.session.add(q)
        db.session.commit()
        if current_user.id != to_id:
            n = Notification(sender_id=current_user.id,
                             receive_id=to_id,
                             target=q.id,
                             target_type='activity',
                             action='comment')
            db.session.add(n)
        return jsonify(msg='success')
    if request.method == 'DELETE':
        q = ActivityQuestion.query.get(request.form.get('id', type=int))
        db.session.delete(q)
        return jsonify(msg='deleted')
    return render_template('activity.html', activity=activity)


@activity.route('/edit/activity/<int:id>', methods=['GET', 'POST'])
@activity.route('/new_activity', methods=['GET', 'POST'])
@login_required
def new_activity(id=None):
    form = ActivityForm()
    # edit activity
    if id:
        a = Activity.query.get(id)
        if a.initiator_id != current_user.id:
            abort(404)
        if form.validate_on_submit():
            a.title = form.title.data
            a.brief = form.brief.data
            db.session.add(a)
            if form.date_expired.data:
                a.set_expired(form.date_expired.data)
            return redirect(url_for('main.index'))
        form.title.default = a.title
        form.brief.default = a.brief
        form.process()
        return render_template('new_activity.html', form=form)
    # new activity
    if form.validate_on_submit():
        new = Activity(title=form.title.data,
                       brief=form.brief.data,
                       initiator_id=current_user.id)
        db.session.add(new)
        db.session.commit()
        if form.date_expired.data:
            new.set_expired(form.date_expired.data)
        return redirect(url_for('main.index'))
    return render_template('new_activity.html', form=form)