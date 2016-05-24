from datetime import datetime
from .. import db

participate = db.Table('participate',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                       db.Column('activity_id', db.Integer, db.ForeignKey('activities.id'))
                       )


class Activity(db.Model):
    """many to many relationship with user"""
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    brief = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())
    date_expired = db.Column(db.DateTime)
    # expired can be decided by date_expired, here we add it in database because
    # we wish we can set the activity to expired manually.
    expired = db.Column(db.Boolean, default=False)
    initiator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # user.activities.all(), activity.participant.all()
    # activity.participant.append(user), db.session.add(activity) to add user
    participants = db.relationship('User',
                                   secondary=participate,
                                   backref=db.backref('activities', lazy='dynamic'),
                                   lazy='dynamic')

    def __init__(self, **kwargs):
        super(Activity, self).__init__(**kwargs)
        now = datetime.now()
        self.date_expired = datetime(now.year, now.month, now.day + 1)

    def set_expired(self, day=1):
        self.date_expired = datetime(self.date_created.year,
                                     self.date_created.month,
                                     self.date_created.day + day)
        db.session.add(self)
        db.session.commit()

