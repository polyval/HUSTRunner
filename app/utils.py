from datetime import datetime
from forum.models import Post, Topic


def rank_hot(topic_id=None):
    """Rank posts by its hot index

    hot_index = (views/10 + comment_count) / (date.now - date.created)
    """
    if not topic_id:
        posts = Post.query.all()
    else:
        posts = Post.query.filter_by(topic_id=topic_id)
    rank = []
    for post in posts:
        hour_gap = (datetime.utcnow() - post.date_created).seconds // 3600
        day_gap, remainder = divmod(hour_gap, 24)
        if day_gap == 0 or remainder:
            day_gap += 1
        hot_index = (post.views / 10 + post.comment_count) / day_gap
        rank.append((post, hot_index))
    rank = sorted(rank, key=lambda x:(x[1], x[0].date_created), reverse=True)
    return [rank[0] for rank in rank]




