from .db_setup import db
    
class Track(db.Model):
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    uri = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    album = db.relationship('Album', backref='tracks')
    artists = db.relationship('Artist', secondary='track_artist', back_populates='tracks')
    playlists = db.relationship('Playlist', secondary='playlist_track', back_populates='tracks')
