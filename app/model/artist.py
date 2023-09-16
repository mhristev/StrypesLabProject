# class Artist:
#     def __init__(self, id, image_url, name, uri):
#         self.id = id
#         self.image_url = image_url
#         self.name = name
#         self.uri = uri
        
from .db_setup import db

class Artist(db.Model):
    id = db.Column(db.String(255),  primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    uri = db.Column(db.String(255), nullable=True)
    tracks = db.relationship('Track', secondary='track_artist', back_populates='artists')

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'uri': self.uri
        }

track_artist = db.Table(
    'track_artist',
    db.Column('track_id', db.String(255), db.ForeignKey('track.id'), primary_key=True),
    db.Column('artist_id', db.String(255), db.ForeignKey('artist.id'), primary_key=True)
)