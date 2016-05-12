from flask import request, abort, jsonify
from flask_login import current_user, login_required

from . import api
from ..forum.models import Comment


@api.route('/comments/vote/', methods=['POST'])
@login_required
def vote_comment():
    print 3
    comment_id = request.form.get('comment_id', type=int)
    print comment_id
    if not comment_id:
        abort(404)
    comment = Comment.query.get_or_404(comment_id)
    print comment
    comment.vote(user_id=current_user.id)
    print comment.votes
    return jsonify(new_votes=comment.votes)
