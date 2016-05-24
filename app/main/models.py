from ..forum.models import Post
from .. import db

tag_img = db.Table('tag_img',
                   db.Column(
                       'img_id', db.Integer, db.ForeignKey('img_faces.id')),
                   db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
                   )


class ImgFace(db.Model):
    __tablename__ = "img_faces"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    tags = db.relationship('Tag',
                           secondary=tag_img,
                           backref=db.backref('imgs', lazy='dynamic'),
                           lazy='dynamic')


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    index = db.Column(db.Integer)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'index': self.index
        }
