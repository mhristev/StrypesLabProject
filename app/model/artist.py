# class Artist:
#     def __init__(self, id, image_url, name, uri):
#         self.id = id
#         self.image_url = image_url
#         self.name = name
#         self.uri = uri
        
from .db_setup import db
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    uri = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    
track_artist = db.Table('track_artist',
    db.Column('track_id', db.Integer, db.ForeignKey('track.id'), primary_key=True),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
)
