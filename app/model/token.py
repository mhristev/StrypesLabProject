from db_setup import db

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    expires_at = db.Column(db.DateTime)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    playlist = db.relationship('Playlist', backref='tokens')
    creator = db.relationship('User', backref='tokens')