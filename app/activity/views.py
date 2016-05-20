from flask import request, jsonify
from flask_login import login_required, current_user
from . import activity
from .. import db
from .models import Activity


@activity.route('/activity', methods=['POST'])
@login_required
def activity():
    action = request.form.get('action')
    activity_id = request.form.get('activity_id', type=int)
    user = current_user._get_current_object()
    a = Activity.query.get(activity_id)
    a.participants.append(user) if action == 'join' else a.participants.remove(user)
    db.session.add(a)
    return jsonify(msg=action + 'success')


