# -*- coding: utf-8 -*-
from datetime import datetime

from app import db
from ..user.models import User


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


class Message(db.Model):
    __tablename__ = "messages"
    # message is mutual
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"),
                                nullable=False)

    # the user who wrote the message
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())

    user = db.relationship("User", lazy="joined")
