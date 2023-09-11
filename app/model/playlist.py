# class Playlist:
#     def __init__(self, id, image_url, name, number_of_tracks):
#         self.id = id
#         self.image_url = image_url
#         self.name = name
#         self.number_of_tracks = number_of_tracks
from .db_setup import db

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    tracks = db.relationship('Track', backref='playlist')
    number_of_tracks = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', backref='playlists')