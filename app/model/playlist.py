# class Playlist:
#     def __init__(self, id, image_url, name, number_of_tracks):
#         self.id = id
#         self.image_url = image_url
#         self.name = name
#         self.number_of_tracks = number_of_tracks
from .db_setup import db

class Playlist(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255))
    number_of_tracks = db.Column(db.Integer)
    tracks = db.relationship('Track', secondary='playlist_track', back_populates='playlists')
    
playlist_track = db.Table(
    'playlist_track',
    db.Column('playlist_id', db.String(255), db.ForeignKey('playlist.id'), primary_key=True),
    db.Column('track_id', db.String(255), db.ForeignKey('track.id'), primary_key=True)
)