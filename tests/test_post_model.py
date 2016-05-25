import unittest
from datetime import datetime
from app.user.models import User
from app.forum.models import Post, Comment
from app import db, create_app


class PostModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_cascade_deletion(self):
        u = User(username='cat', email='cat@qq.com', password='cat')
        db.session.add(u)
        db.session.commit()
        p = Post(author=u, content_html='test', title='test')
        db.session.add(p)
        db.session.commit()
        c = Comment(content_html='test', post=p, author=u)
        db.session.add(c)
        db.session.commit()
        db.session.delete(p)
        self.assertTrue(Post.query.count() == 0)
        self.assertTrue(Comment.query.count() == 0)