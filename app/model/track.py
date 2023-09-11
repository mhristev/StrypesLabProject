from .db_setup import db
# class Track:
#     def __init__(self, id, name, artists, uri, image_url):
#         self.id = id
#         self.name = name
#         self.artists = artists
#         self.uri = uri
#         self.image_url = image_url

    
playlist_track = db.Table(
    'playlist_track',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
)

class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    uri = db.Column(db.String(255))
    image_url = db.Column(db.String(255))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    artists = db.relationship('Artist', secondary='track_artist', backref='tracks')
    
    playlists = db.relationship('Playlist', secondary=playlist_track, backref='tracks')
    album = db.relationship('Album', backref='tracks')
    


