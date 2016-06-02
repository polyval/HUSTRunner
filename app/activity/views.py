from flask import request, jsonify, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import activity
from .. import db
from .models import Activity
from .forms import ActivityForm


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


@activity.route('/activity/<int:id>')
@login_required
def view_activity(id):
    activity = Activity.query.get(id)
    return render_template('activity.html', activity=activity)


@activity.route('/new_activity', methods=['GET', 'POST'])
@login_required
def new_activity():
    form = ActivityForm()
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

# TODO: view activity
