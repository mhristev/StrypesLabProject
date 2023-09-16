from flask import Flask, request, url_for, session, redirect, render_template, jsonify
import os
from clients.spotify_client import SpotifyClient
from clients.deezer_client import DeezerClient
from functools import wraps
from flask_login import LoginManager
import uuid
from flask_login import login_user, login_required, logout_user, current_user

from model.track import Track
from model.artist import Artist
from model.album import Album
from model.playlist import Playlist
from model.token import Token
from model.user import User
import pytz

from model.user import db
from datetime import datetime, timedelta, timezone

TOKEN_INFO_SPOTIFY = 'token_info_spotify'
TOKEN_INFO_DEEZER = 'token_info_deezer'
TOKEN_DEEZER_EXPIRES_ON = 'token_deezer_expires_on'
DOMAIN_URL = "http://127.0.0.1:5000/"

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

DEEZER_APP_ID = os.getenv("DEEZER_APP_ID")
DEEZER_CLIENT_SECRET = os.getenv("DEEZER_CLIENT_SECRET")
DEEZER_REDIRECT_URI = os.getenv("DEEZER_REDIRECT_URI")

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

login_manager = LoginManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.app_context().push()
db.create_all()

     

@login_manager.user_loader
def get_user(id):
    return User.query.filter_by(id=id).first()


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if the user is authenticated with either Spotify or Deezer
        if 'token_info_spotify' in session or 'token_info_deezer' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated

def get_spotify_client(session_token_info):
    return SpotifyClient(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, session_token_info=session_token_info)

def get_deezer_client(session_token_info):
    return DeezerClient(DEEZER_APP_ID, DEEZER_CLIENT_SECRET, DEEZER_REDIRECT_URI, session_token_info=session_token_info)

def check_for_expired_tokens():
    token_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_deezer = session.get(TOKEN_INFO_DEEZER)
    print("Checking for expired tokens")

    if token_spotify:
        spotify_client = get_spotify_client(session_token_info=token_spotify)
        session[TOKEN_INFO_SPOTIFY] = spotify_client.refresh_token_if_needed()  
    if token_deezer:
        current_time = datetime.now()
        d = str(session.get(TOKEN_DEEZER_EXPIRES_ON))
        given_datetime = datetime.fromisoformat(d)
        current_time = datetime.now(pytz.utc)
        print(current_time)
        print (current_time > given_datetime)
    
       
        if current_time >= given_datetime:
            print("Expired token")
            session[TOKEN_INFO_DEEZER] = None
        else:
            print(given_datetime)
            print("Token not expired")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/generate_token', methods=['GET', 'POST'])
def generate_token():
    playlist_id = request.args.get('playlist_id')
    playlist_name = request.args.get('playlist_name')
    platform = request.args.get('platform')
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)

    if not playlist_id or not playlist_name:
        return redirect(url_for('playlists'))
    tracks = []
    if token_info_spotify and platform.lower() == "spotify":
        spotify_client = get_spotify_client(token_info_spotify)
        tracks = spotify_client.get_tracks_in_playlist(playlist_id=playlist_id)
    elif token_info_deezer and platform.lower() == "deezer":
        deezer_client = get_deezer_client(token_info_deezer)
        tracks = deezer_client.get_tracks_in_playlist(playlist_id=playlist_id)
    
    playlist = Playlist(name=playlist_name, id=str(uuid.uuid4()))

    for track in tracks:
        existing_track = Track.query.filter_by(name=track.name).first()
        if existing_track:
            for artist in existing_track.artists:
                artist = Artist.query.filter_by(name=artist.name).first()
                if not artist:
                    artist = Artist(id=str(uuid.uuid4()), name=artist.name)
                    db.session.add(artist)

                if artist not in existing_track.artists:
                    existing_track.artists.append(artist)
  
                existing_track.album_id = track.album.id
                
                if existing_track not in playlist.tracks:
                    playlist.tracks.append(existing_track)
        else:
            album = Album.query.get(track.album.id)
            if not album:
                album = Album(id=track.album.id, name=track.album.name)
                db.session.add(album)
                    
            new_track = Track(id=track.id, name=track.name, album=album, uri=track.uri, image_url=track.image_url)
            for a in track.artists:
                artist = Artist.query.filter_by(name=a.name).first()
                if not artist:
                    artist = Artist(id=str(uuid.uuid4()), name=a.name)
                    db.session.add(artist)
                
                new_track.artists.append(artist)
                if new_track not in playlist.tracks:
                    playlist.tracks.append(new_track)
                db.session.add(new_track)
    
    db.session.add(playlist)
    
    
    token_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(days=1)
    new_token = Token(
        id=token_id,
        created_at=created_at,
        expires_at=expires_at,
        playlist=playlist,  
        creator_id=current_user.id 
    )
    db.session.add(new_token)

    db.session.commit()
    url = DOMAIN_URL + "shared/" + token_id

    return render_template("shared_playlist_preview.html", token=new_token, url=url)

@app.route('/shared/<token_id>', methods=['GET'])
def view_playlist(token_id):
    token = Token.query.filter_by(id=token_id).first()

    if not token:
        return jsonify({'error': 'Playlist not found'}), 404

    current_time = datetime.utcnow()
    print(current_time)
    if current_time > token.expires_at:
        return jsonify({'error': 'Token has expired'}), 403

    url = DOMAIN_URL + "shared/" + token_id
    return render_template("shared_playlist_preview.html", token=token, url=url)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/auth_spotify')
def auth_spotify():
    spotify_client = get_spotify_client(session_token_info=None)
    auth_url = spotify_client.login()
    return redirect(auth_url)

@app.route('/auth_deezer')
def auth_deezer():
    deezer_client = get_deezer_client(session_token_info=None)
    auth_url = deezer_client.authorization_url()
    return redirect(auth_url)

@app.route("/callback", methods=["GET"])
def callback(): 
    code = request.args.get('code')
    deezer_client = get_deezer_client(session_token_info=None)
    access_token = deezer_client.fetch_token(code)
    if access_token:
        deezer_client = get_deezer_client(session_token_info=access_token)
        user = deezer_client.get_current_user()
        user_db = User.query.filter_by(email=user.email).first()
        if user_db is None:
            user_db = User(email=user.email, display_name=user.display_name, id=user.id)
            db.session.add(user_db)
            db.session.commit()
        login_user(user_db)
        expires_in_seconds = int(access_token.split("expires=")[1])
        expiration_time = datetime.now(pytz.utc) + timedelta(seconds=expires_in_seconds)
       
        session[TOKEN_DEEZER_EXPIRES_ON] = expiration_time
        session[TOKEN_INFO_DEEZER] = access_token
        return redirect(url_for('playlists'))
    else:
        return "Failed to retrieve access token."
    
    
@app.route('/redirect')
def redirect_page():
    code = request.args.get('code')
    spotify_client = get_spotify_client(session_token_info=None)
    token_info = spotify_client.exchange_code_for_token(code)
    if token_info:
        spotify_client = get_spotify_client(session_token_info=token_info)
        user = spotify_client.get_current_user()
      
        user_db = User.query.filter_by(email=user.email).first()

        if user_db is None:
            user_db = User(email=user.email, display_name=user.display_name, id=user.id)
            db.session.add(user_db)
            db.session.commit()
        
        login_user(user_db)
        session[TOKEN_INFO_SPOTIFY] = token_info
        return redirect(url_for('playlists'))
    else:
        return "Failed to retrieve access token."



@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    form_name = request.form['form_name']
    new_playlist_name = request.form['new_playlist_name']
    playlist_id = None
    if form_name.lower() == "spotify":
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        playlist_id = spotify_client.create_playlist(name=new_playlist_name.strip())
    elif form_name.lower() == "deezer":
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        playlist_id = deezer_client.create_playlist(name=new_playlist_name.strip())
    image_url = "https://e-cdns-images.dzcdn.net/images/cover//500x500-000000-80-0-0.jpg"
    
    data = { 
        'playlist_id': playlist_id,
        'playlist_name': new_playlist_name,
        'image_url': image_url,
        'view_url': url_for('view', playlist_id=playlist_id, platform=form_name.lower()),
        'delete_url': url_for('delete', platform=form_name.lower(), playlist_id=playlist_id),
        'platform' : form_name.lower()
    }
    return jsonify(data=data), 200

@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    platform = request.json.get('platform')
    track_indentifier = request.json.get('track_indentifier')
    playlist_id = request.json.get('playlist_id')
    track = None
    if platform.lower() == 'spotify':
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        spotify_client.add_track_uri_to_playlist(track_uri=track_indentifier, playlist_id=playlist_id)
        track = spotify_client.get_track(track_uri=track_indentifier)
        
    elif platform.lower() == 'deezer':
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        deezer_client.add_track_id_to_playlist(playlist_id=playlist_id, track_id=track_indentifier)
        track = deezer_client.get_track(track_id=track_indentifier)
    serialized_data =  {
            'id': track.id,
            'name': track.name,
            'artists': [artist.serialize() for artist in track.artists],
            'uri' : track.uri,
            'image_url': track.image_url,
            "album_name" : track.album.name
        }
    return jsonify(data=serialized_data), 200

@app.route('/logout')
def logout():
    session.pop(TOKEN_INFO_SPOTIFY, None)
    session.pop(TOKEN_INFO_DEEZER, None)
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    spotify_client = get_spotify_client(session_token_info=token_info_spotify)
    artists, genres_list = spotify_client.get_current_user_top_artists_genres()
    all_genres = [genre for sublist in genres_list for genre in sublist]
    genre_counts = Counter(all_genres)
    top_3_genres = genre_counts.most_common(5)
    return render_template('profile.html', artists=artists, genres=top_3_genres)


@app.route('/recommendations')
@login_required
def recommendations():
    check_for_expired_tokens()
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    
    recommended_tracks = []
    if token_info_spotify:
        spotify_client = get_spotify_client(token_info_spotify)
        sp_tracks = spotify_client.get_current_user_recommended_tracks()
        recommended_tracks += sp_tracks
        
    if token_info_deezer:
        deezer_client = get_deezer_client(token_info_deezer)
        dz_tracks = deezer_client.get_current_user_recommended_tracks()
        recommended_tracks += dz_tracks

    return render_template("recommendations.html", recommended_tracks=recommended_tracks)


@app.route('/playlists')
@login_required
def playlists():
    print(session.get(TOKEN_INFO_DEEZER))
    check_for_expired_tokens()
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    spotify_playlists = None
    deezer_playlists = None
    
    if token_info_deezer:
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        deezer_playlists = deezer_client.get_playlists_curr_user()
    if token_info_spotify:
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        spotify_playlists = spotify_client.get_playlists_for_current_user()
        
    return render_template('playlists.html', spotify_playlists=spotify_playlists, deezer_playlists=deezer_playlists)

@app.route('/view/<playlist_id>/<platform>/<playlist_name>', methods=['GET'])
def view(playlist_id, platform, playlist_name):
    tracks = []
    print("AAAA", playlist_id)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    
    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        tracks = spotify_client.get_tracks_in_playlist(playlist_id=playlist_id)
    elif platform.lower() == "deezer":
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        tracks = deezer_client.get_tracks_in_playlist(playlist_id=playlist_id)

    return render_template("playlistView.html", tracks=tracks, playlist_id=playlist_id, platform=platform.lower(), playlist_name=playlist_name)


@app.route('/delete/<platform>/<playlist_id>', methods=['POST', 'GET'])
def delete(platform, playlist_id):
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)

    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        spotify_client.unfollow_playlist(playlist_id=playlist_id)
    elif platform.lower() == "deezer":
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        deezer_client.delete_playlist(playlist_id=playlist_id)

    return '', 200
    
@app.route('/search_tracks', methods=['POST'])
def search():
    search_query = request.json.get('searchQuery')
    platform = request.json.get('platform')
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    found_tracks = []

    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        found_tracks = spotify_client.search_for_tracks_with_name(search_query.strip())
    elif platform.lower() == "deezer":
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        found_tracks = deezer_client.search_for_tracks_with_name(search_query.strip())
    
    serialized_results = [
        {
            'id': track.id,
            'name': track.name,
            'artists': [artist.serialize() for artist in track.artists],
            'uri' : track.uri,
            'image_url': track.image_url,
            'album_name': track.album.name
        }
        for track in found_tracks
    ]

    return jsonify(results=serialized_results)

@app.route('/remove_track_from_playlist', methods=['POST'])
def remove_track_from_playlist():
    track_id = request.json.get('track_id')
    platform = request.json.get('platform')
    playlist_id = request.json.get('playlist_id')
    
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    if platform == 'spotify':
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        spotify_client.remove_track_from_playlist(track_id, playlist_id)
    elif platform == 'deezer':
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        deezer_client.remove_track_from_playlist(playlist_id=playlist_id, track_id=track_id)
    return jsonify(), 200


@app.route('/transfer_shared_playlist', methods=['POST'])
def transfer_shared_playlist():
    platform = request.form['platform']
    token_id = request.form['token_id']
    token = Token.query.filter_by(id=token_id).first()

    if not token:
        return jsonify({'error': 'Playlist not found'}), 404

    current_time = datetime.utcnow()
    if current_time > token.expires_at:
        return jsonify({'error': 'Token has expired'}), 403
    
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    if token_info_spotify and platform.lower() == "spotify":
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        tracks = token.playlist.tracks
        playlist_name = token.playlist.name
        new_playlist_id = spotify_client.create_playlist(playlist_name)
        spotify_client.add_tracks_to_playlist(tracks=tracks, playlist_id=new_playlist_id)
    elif token_info_deezer and platform.lower() == "deezer":
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        tracks = token.playlist.tracks
        playlist_name = token.playlist.name
        new_playlist_id = deezer_client.create_playlist(playlist_name)
        deezer_client.add_tracks_to_playlist(tracks=tracks, playlist_id=new_playlist_id)
    return redirect(url_for("playlists"))


@app.route('/transfer_playlist_deezer_to_spotify', methods=['POST'])
def transfer_playlist_deezer_to_spotify():
    
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    spotify_client = get_spotify_client(session_token_info=token_info_spotify)
    deezer_client = get_deezer_client(session_token_info=token_info_deezer)
    
    playlist_id = request.json.get("playlist_id")
    name = request.json.get("name")
    
    tracks = deezer_client.get_tracks_in_playlist(playlist_id)
    
    new_playlist_id = spotify_client.create_playlist(name)
    spotify_client.add_tracks_to_playlist(tracks=tracks, playlist_id=new_playlist_id)
    playlist = spotify_client.get_playlist(new_playlist_id)

    data = \
    {
        'playlist_id': playlist.id,
        'playlist_name': playlist.name,
        'number_of_tracks': playlist.number_of_tracks,
        'image_url': playlist.image_url, 
        'view_url': url_for('view', playlist_id=playlist.id, platform='spotify', playlist_name=playlist.name),
        'delete_url': url_for('delete', platform='spotify', playlist_id=playlist.id),
        'platform' : 'spotify'
    }
    return jsonify(data=data), 200


@app.route('/transfer_playlist_spotify_to_deezer', methods=['POST'])
def transfer_playlist_spotify_to_deezer():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    spotify_client = get_spotify_client(session_token_info=token_info_spotify)
    
    playlist_id = request.json.get("playlist_id")
    name = request.json.get("name")
    
    tracks = spotify_client.get_tracks_in_playlist(playlist_id)
    #TODO napravi offset i limit shoto max e 100 ako playlista e > 100 stava meh
    deezer_client = get_deezer_client(session_token_info=token_info_deezer)
    new_playlist_id = deezer_client.create_playlist(name)
    deezer_client.add_tracks_to_playlist(new_playlist_id, tracks)
    playlist = deezer_client.get_playlist_info(new_playlist_id)
    
    data = \
    {
        'playlist_id': playlist.id,
        'playlist_name': playlist.name,
        'number_of_tracks': playlist.number_of_tracks,
        'image_url': playlist.image_url, 
        'view_url': url_for('view', playlist_id=playlist.id, platform='deezer', playlist_name=playlist.name),
        'delete_url': url_for('delete', platform='deezer', playlist_id=playlist.id),
        'platform' : 'deezer'
    }
    return jsonify(data=data), 200
    

if __name__ == '__main__':
    app.config['SESSION_COOKIE_NAME'] = 'Cookie'
    app.secret_key = 'YOUR_SECRET_KEY1'
    app.run(debug=True)
