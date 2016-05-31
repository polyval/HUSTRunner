# -*- coding: utf-8 -*-
from datetime import datetime
from itertools import groupby

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy import func, and_

from app import db
from ..activity.models import Activity
from .. import login_manager


class Permission:
    FOLLOW = 0x01  # hex representation, equals to 0b00000001
    COMMENT = 0X02
    STICK = 0X03
    POST = 0x04
    UNBAN = 0x05
    BAN = 0x06
    MODERATE_POSTS = 0X07
    MODERATE_COMMENTS = 0X08
    ADMINISTER = 0X80


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # backref add role attribute to User model, this attribute can use to
    # access Role model
    user = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.POST, True),
            'Moderator_deputy': (Permission.FOLLOW |
                                 Permission.COMMENT |
                                 Permission.STICK |
                                 Permission.POST |
                                 Permission.MODERATE_COMMENTS, False),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.STICK |
                          Permission.POST |
                          Permission.UNBAN |
                          Permission.BAN |
                          Permission.MODERATE_COMMENTS |
                          Permission.MODERATE_POSTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class Follow(db.Model):
    __tablename__ = "follows"

    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())

    @staticmethod
    def generate_fake(count=50):
        from random import seed, randint
        seed()
        user_count = User.query.count()
        for i in range(count):
            u1 = User.query.offset(randint(0, user_count - 1)).first()
            u2 = User.query.offset(randint(0, user_count - 1)).first()
            if u1.is_following(u2):
                continue
            f = Follow(follower=u1, followed=u2)
            db.session.add(f)
        db.session.commit()


class User(UserMixin, db.Model):

    """
    UserMixin provides default implementations for
    is_authenticated, is_active, is_anonymous, get_id
    methods
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    _password = db.Column('password', db.String(120), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    student_id = db.Column(db.String(30), unique=True)
    name = db.Column(db.String(100))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    gender = db.Column(db.String(10))
    school = db.Column(db.String(100))
    avatar = db.Column(db.String(200), default='/static/avatar/profile.jpg')
    signature = db.Column(db.String(100))
    about_me = db.Column(db.Text)
    # TODO: label marathon, half marathon, for future
    # title = db.Column(db.String(50))
    # one to many, add author attribute to Post, this attribute refers to User
    # Object
    posts = db.relationship("Post", backref="author", lazy="dynamic")
    # topics = db.relationship("Topic", backref="user", lazy="dynamic")
    comments = db.relationship("Comment", backref="author", lazy="dynamic")
    post_count = db.Column(db.Integer, default=0)

    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    initiate_activities = db.relationship('Activity',
                                          foreign_keys=[Activity.initiator_id],
                                          backref='initiator',
                                          lazy='dynamic')

    notify_settings = db.relationship("NotifyConfig",
                                      backref=db.backref('user', uselist=False),
                                      lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASK_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @staticmethod
    def generate_fake(count=50):
        """Generate fake users for testing"""
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(with_num=True),
                     password='hustrunner',
                     confirmed=True,
                     signature=forgery_py.lorem_ipsum.word(),
                     date_joined=forgery_py.date.date(past=True))
            db.session.add(u)
            # in case there are two identical users
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @property
    def days_registered(self):
        """Returns the amount of days the user is registered"""
        days_registered = (datetime.utcnow() - self.date_joined).days
        if not days_registered:
            return 1
        return days_registered

    @property
    def notify_count(self):
        return self.get_notify_count()

    @property
    def vote_notify_count(self):
        return self.action_notify_count(action='vote')

    @property
    def comment_notify_count(self):
        return self.action_notify_count(action='comment')

    @property
    def follow_notify_count(self):
        return self.action_notify_count(action='follow')

    @property
    def unread_message_count(self):
        """
        Get the count of unread personal messages,
        multiple messages from one person merges as one.
        """
        from ..message.models import Conversation
        return Conversation.query.filter_by(user_id=self.id, unread=True).count()

    @property
    def unread_notifications(self):
        return self.get_unread_notifications()

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY', expiration])
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def get_unread_notifications(self):
        """
        get unread notifications grouped by day, target_type, target_id
        :return list
            [day, target_type, target, notification...]
        """
        # avoid circular import
        from ..message.models import Notification
        # get all unview notifications
        unview = Notification.query.filter(Notification.receive_id == self.id,
                                           Notification.view == False).all()
        messy = []
        for notif in unview:
            messy.append(
                (notif.date_created.strftime('%Y-%m-%d'), notif.action, notif.entity, notif))
        messy.sort(key=lambda x: (x[0], x[1], x[2]))
        unread_notifications = []
        for key, group in groupby(messy, key=lambda x: (x[0], x[1], x[2])):
            unread_notifications.append(
                {'date': key[0], 'action': key[1], 'entity': key[2],
                 'notify': [noti[3] for noti in group]})
        return unread_notifications

    def get_notify_count(self):
        from ..message.models import Notification
        notify_count = db.session.query(func.count(Notification.id)).\
            filter(Notification.unread == True,
                   Notification.receive_id == self.id).\
            group_by(func.date(Notification.date_created),
                     Notification.action,
                     Notification.target,
                     Notification.target_type).count()
        return notify_count

    def action_notify_count(self, action='vote'):
        from ..message.models import Notification
        action_notify_count = db.session.query(func.count(Notification.id)).\
            filter(Notification.unread == True,
                   Notification.receive_id == self.id,
                   Notification.action == action).\
            group_by(func.date(Notification.date_created),
                     Notification.target,
                     Notification.target_type).count()
        return action_notify_count

    def has_join(self, activity):
        return True if User.query.filter(User.activities.contains(activity),
                                         User.id == self.id).first() else False

    def can(self, permissions):
        """ Check whether the user has permissions"""
        return self.role is not None and (self.role.permissions & permissions) == permissions
        # bitwise operation

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        """get the last time the user visit the website"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def __repr__(self):
        return '<User %r>' % self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):

    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
