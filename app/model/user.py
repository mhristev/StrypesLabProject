from .db_setup import db
from flask_security import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.String(100), primary_key=True)
    display_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    playlists = db.relationship('Playlist', backref='user')
    
    def __init__(self, id, display_name, email):
        self.id = id
        self.display_name = display_name
        self.email = email
    
    def __repr__(self):
        return f'<User {self.display_name}>'
    
    def is_active(self):
        return True
    
    def get_id(self):   
        return self.id
    
    
# class Token(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
#     expires_at = db.Column(db.DateTime)
#     playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
#     creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
#     playlist = db.relationship('Playlist', backref='tokens')
#     creator = db.relationship('User', backref='tokens')

# class Playlist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     image_url = db.Column(db.String(255))
#     tracks = db.relationship('Track', backref='playlist')
#     number_of_tracks = db.Column(db.Integer)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# class Album(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))


# playlist_track = db.Table(
#     'playlist_track',
#     db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
#     db.Column('track_id', db.Integer, db.ForeignKey('track.id'))
# )

# class Track(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     uri = db.Column(db.String(255))
#     image_url = db.Column(db.String(255))
#     album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
#     artists = db.relationship('Artist', secondary='track_artist')

# class Artist(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255))
#     uri = db.Column(db.String(255))
#     image_url = db.Column(db.String(255))

# track_artist = db.Table('track_artist',
#     db.Column('track_id', db.Integer, db.ForeignKey('track.id'), primary_key=True),
#     db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True)
# )

