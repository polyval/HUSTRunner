from flask import request, abort, jsonify
from flask_login import current_user, login_required
from . import api
from app import db
from ..forum.models import Comment
from ..user.models import User, Permission
from ..message.models import Notification
from ..main.models import ImgFace, Tag
from ..decorators import permission_required


@api.route('/comments/vote', methods=['POST'])
@login_required
def vote_comment():
    comment_id = request.form.get('comment_id', type=int)
    if not comment_id:
        abort(404)
    comment = Comment.query.get_or_404(comment_id)
    comment.vote(user_id=current_user.id)
    notify = Notification(sender_id=current_user.id,
                          receive_id=comment.author.id,
                          target=comment.id,
                          target_type='comment',
                          action='vote')
    db.session.add(notify)
    return jsonify(new_votes=comment.votes)


@api.route('/follow', methods=['POST'])
@login_required
def toggle_follow():
    user_id = request.form.get('user_id', type=int)
    # unfollow or follow
    unfollow = request.form.get('unfollow')
    # user to follow or unfollow
    to_user = User.query.get_or_404(user_id)
    user = current_user._get_current_object()
    if unfollow == 'true':
        user.unfollow(user=to_user)
    else:
        user.follow(user=to_user)
        notify = Notification(sender_id=user.id,
                              receive_id=to_user.id,
                              target=to_user.id,
                              target_type='user',
                              action='follow')
        db.session.add(notify)
    return jsonify(msg=0)


@api.route('/comments/<int:id>', methods=['DELETE'])
@permission_required(Permission.MODERATE_COMMENTS)
def delete_comment(id):
    Comment.query.filter_by(id=id).delete()
    Comment.query.filter_by(parent_id=id).delete()
    return jsonify(delete=id)


@api.route('/notification', methods=['POST'])
@login_required
def noti_count():
    # get the category of notifications
    action = request.form.get('action')
    Notification.query.filter(Notification.receive_id == current_user.id,
                              Notification.action == action).update({Notification.unread: False})
    db.session.commit()
    return jsonify(new_count=current_user.notify_count)


@api.route('/faces', methods=['GET', 'POST'])
@login_required
def face():
    img_url = request.form.get('img_url') or request.args.get('img_url')
    img = ImgFace.query.filter_by(url=img_url).first()
    # save img info to database
    if not img:
        img = ImgFace(url=img_url)
        db.session.add(img)
        db.session.commit()
    if request.method == 'GET':
        tags = img.tags.all()
        return jsonify(tags=[i.serialize for i in tags])


@api.route('/faces/tag', methods=['GET', 'POST'])
@login_required
def tag_face():
    url = request.form.get('url')
    img = ImgFace.query.filter_by(url=url).first()
    new_tag = Tag(
        name=request.form.get('tag'), index=request.form.get('index'))
    db.session.add(new_tag)
    db.session.commit()
    img.tags.append(new_tag)
    return jsonify(tag=request.form.get('tag'))
