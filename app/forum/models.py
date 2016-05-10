# -*- coding: utf-8 -*-
from datetime import datetime
from slugify import slugify

from ..user.models import User
from app import db


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    content_html = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    date_modified = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    hot_index = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=50):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        topic_count = Topic.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            topic = Topic.query.offset(randint(0, topic_count - 1)).first()
            p = Post(content_html=forgery_py.lorem_ipsum.paragraph(html=True),
                     title=forgery_py.lorem_ipsum.title(),
                     date_created=forgery_py.date.date(past=True),
                     views=randint(0, 1000),
                     author=u,
                     topic=topic)
            p.slug = p.slugify()
            db.session.add(p)
        db.session.commit()

    @staticmethod
    def rank_hot(topic_id=None):
        """Rank posts by its hot index

            hot_index = (views/10 + comment_count) / (date.now - date.created)
        """
        if not topic_id:
            posts = Post.query.all()
        else:
            posts = Post.query.filter_by(topic_id=topic_id)
        for post in posts:
            hour_gap = (datetime.utcnow() - post.date_created).seconds // 3600
            day_gap, remainder = divmod(hour_gap, 24)
            if day_gap == 0 or remainder:
                day_gap += 1
            hot_index = (post.views / 10 + post.comments.count()) / day_gap
            post.hot_index = hot_index
            db.session.add(post)
        db.session.commit()

    def slugify(self):
        """Return unique slug for post"""
        slug_title = slugify(self.title)
        if Post.query.filter_by(slug=slug_title).first():
            date = datetime.today()
            slug = '{0:s}/{1:d}/{2:d}/{3:d}/{4:s}'.format(
                str(date.year)[2:], date.month, date.day, date.microsecond, slug_title)
            if Post.query.filter_by(slug=slug).first():
                slug = '{0:d}/{1:d}/{2:d}/{3:d}/{4:s}'.format(
                    self.author_id, date.year, date.month, date.day, slug_title
                )
            return slug
        return slug_title


class Topic(db.Model):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # add topic attribute to Post model for accessing Topic model
    posts = db.relationship("Post", backref="topic", lazy="dynamic")
    post_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow())
    views = db.Column(db.Integer, default=0)

    @staticmethod
    def insert_topic(titles=('running', 'tips', 'competition', 'water')):
        for title in titles:
            topic = Topic(title=title)
            db.session.add(topic)
        db.session.commit()

    def __repr__(self):
        return '<Topic %r>' % self.title


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content_html = db.Column(db.Text)
    date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    children = db.relationship("Comment", backref=db.backref('parent',
                    remote_side=[id]), lazy='dynamic')
    # TODO: votes in template
    votes = db.Column(db.Integer, default=1)

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        post_count = Post.query.count()
        # parent comments
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post.query.offset(randint(0, post_count - 1)).first()
            c = Comment(content_html=forgery_py.lorem_ipsum.paragraph(html=True),
                        date_created=forgery_py.date.date(past=True),
                        author=u,
                        post=p)
            db.session.add(c)
        db.session.commit()
        # child comments
        for i in range(3):
            for i in range(count):
                u = User.query.offset(randint(0, user_count - 1)).first()
                parent_comments_count = Comment.query.count()
                parent_comment = Comment.query.offset(randint(0, parent_comments_count - 1)).first()
                c = Comment(content_html=forgery_py.lorem_ipsum.paragraph(html=True),
                            date_created=forgery_py.date.date(past=True),
                            author=u,
                            parent=parent_comment)
                db.session.add(c)
            db.session.commit()

