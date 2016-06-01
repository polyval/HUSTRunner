# -*- coding: utf-8 -*-
from datetime import datetime

from app import db
from ..forum.models import Post, Comment, CommentVote


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    # unread is here not in message model because conversation has directions
    unread = db.Column(db.Boolean, nullable=False, default=True)

    messages = db.relationship(
        "Message", lazy="joined", backref="conversation",
        primaryjoin="Message.conversation_id == Conversation.id",
        order_by="asc(Message.id)",
        cascade="all, delete-orphan"
    )

    # this is actually the users message box
    user = db.relationship("User", lazy="joined", foreign_keys=[user_id])
    # the user to whom the conversation is addressed
    to_user = db.relationship("User", lazy="joined", foreign_keys=[to_user_id])
    # the user who sent the message
    from_user = db.relationship("User", lazy="joined",
                                foreign_keys=[from_user_id])

    @property
    def first_message(self):
        """Returns the first message object."""
        return self.messages[0]

    @property
    def last_message(self):
        """Returns the last message object."""
        return self.messages[-1]

    @property
    def has_message(self):
        return True if self.messages else False


class Message(db.Model):
    __tablename__ = "messages"
    # two-way message
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"),
                                nullable=False)

    # the user who wrote the message
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    user = db.relationship("User", lazy="joined")


class Notification(db.Model):

    """
    target_type: post, comment, user
    action: vote，comment，follow
    target: post_id, comment_id, user_id
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    receive_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    target = db.Column(db.Integer, nullable=False)
    target_type = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(20))
    unread = db.Column(db.Boolean, default=True)
    view = db.Column(db.Boolean, default=False)

    @property
    def entity(self):
        return self.get_object()

    @property
    def sender(self):
        return self.get_sender()

    def get_sender(self):
        from ..user.models import User
        return User.query.get(self.sender_id)

    def get_object(self):
        from ..user.models import User
        if self.target_type == 'post':
            entity = Post.query.get(self.target)
        elif self.target_type == 'comment':
            entity = Comment.query.get(self.target)
        else:
            entity = User.query.get(self.target)
        return entity

    @staticmethod
    def generate_fake(count=20):
        # TODO: DRY IT
        import forgery_py
        from random import randint, seed
        from ..user.models import User
        seed()
        p_count = Post.query.count()
        c_count = Comment.query.count()
        u_count = User.query.count()
        for i in range(count):
            p_notify = Notification(date_created=forgery_py.date.date(past=True),
                                    sender_id=randint(0, u_count - 1),
                                    receive_id=1,
                                    target=randint(0, p_count - 1),
                                    target_type='post',
                                    action='vote' if randint(
                                        0, count) % 2 else 'comment',
                                    unread=True if randint(
                                        0, count) % 2 else False,
                                    )
            c_notify = Notification(date_created=forgery_py.date.date(past=True),
                                    sender_id=randint(0, u_count - 1),
                                    receive_id=1,
                                    target=randint(0, c_count - 1),
                                    target_type='comment',
                                    action='vote' if randint(
                                        0, count) % 2 else 'comment',
                                    unread=True if randint(
                                        0, count) % 2 else False,
                                    )
            u_notify = Notification(date_created=forgery_py.date.date(past=True),
                                    sender_id=randint(0, u_count - 1),
                                    receive_id=1,
                                    target=randint(0, u_count - 1),
                                    action='follow',
                                    target_type='user',
                                    unread=True if randint(
                                        0, count) % 2 else False,
                                    )
            db.session.add(p_notify)
            db.session.add(c_notify)
            db.session.add(u_notify)
        db.session.commit()


class NotifyConfig(db.Model):
    __tablename__ = "notifysettings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    # receive personal message from any user
    pm_all = db.Column(db.Boolean, default=True)
    be_followed = db.Column(db.Boolean, default=True)
    # 0, receive all 1, all from person I followed 2, block
    post_be_voted = db.Column(db.Integer, default=0)
    comment_be_voted = db.Column(db.Integer, default=0)
    comment = db.Column(db.Integer, default=0)
