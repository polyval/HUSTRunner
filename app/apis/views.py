from flask import request, abort, jsonify, Response
from flask_login import current_user, login_required

from . import api
from ..forum.models import Comment
from ..user.models import User, Permission
from ..decorators import permission_required


@api.route('/comments/vote', methods=['POST'])
@login_required
def vote_comment():
    comment_id = request.form.get('comment_id', type=int)
    if not comment_id:
        abort(404)
    comment = Comment.query.get_or_404(comment_id)
    comment.vote(user_id=current_user.id)
    return jsonify(new_votes=comment.votes)

@api.route('/follow', methods=['POST'])
@login_required
def toggle_follow():
    user_id = request.form.get('user_id', type=int)
    unfollow = request.form.get('unfollow')
    print unfollow
    to_user = User.query.get_or_404(user_id)
    user = current_user._get_current_object()
    if unfollow == 'true':
        user.unfollow(user=to_user)
    else:
        user.follow(user=to_user)
        print unfollow
    return jsonify(msg=0)

@api.route('/comments/<int:id>', methods=['DELETE'])
@permission_required(Permission.MODERATE_COMMENTS)
def delete_comment(id):
    Comment.query.filter_by(id=id).delete()
    return jsonify(delete=id)