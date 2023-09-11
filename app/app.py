from flask import Flask, request, url_for, session, redirect, render_template, jsonify
import os
from model.spotify_client import SpotifyClient
from model.deezer_client import DeezerClient
import time
from functools import wraps
from collections import Counter
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
import uuid
from flask_login import login_user, login_required, logout_user, current_user
from model.user import User
from model.playlist import Playlist
from model.track import Track
from model.user import db
import secrets

TOKEN_INFO_SPOTIFY = 'token_info_spotify'
TOKEN_INFO_DEEZER = 'token_info_deezer'

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
    print("VALIDATION")
    user = User.query.filter_by(id=id).first()
    print(user.email, user.display_name)
    print(id)
    # Retrieve the user from your database using the user_id
    return User.query.filter_by(id=id).first()


# @app.before_first_request
# def create_database():



@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


def test():
    user = User(display_name="testname", email="email", password="password")
    db.session.add(user)
    db.session.commit()
        

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
        print("TOKEN DW")
        deezer_client = get_deezer_client(session_token_info=token_deezer)
        if deezer_client.is_token_expired():
            print("expired")
            session[TOKEN_INFO_DEEZER] = None
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            print(session.get(TOKEN_INFO_DEEZER))


@app.route('/')
def index():
    check_for_expired_tokens()
    
    token_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_deezer = session.get(TOKEN_INFO_DEEZER)
    if token_spotify == None and token_deezer == None:
        return render_template("login.html")
    
    # if current_user.is_authenticated == False:
    #     test = User.query.first()
    #     login_user(test)
    #     print('AAAAA')
    #     print(current_user.id)
    #     print('AAAAA')  
    return redirect(url_for('playlists'))
    # return render_template("base.html")


@app.route('/generate_token', methods=['GET', 'POST'])
def generate_token():
    playlist_id = request.args.get('playlist_id')
    playlist_name = request.args.get('playlist_name')
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    # Check if playlist_id and playlist_name are provided
    if not playlist_id or not playlist_name:
        return redirect(url_for('index'))
    
    token = secrets.token_urlsafe(16)
    spotify_client = get_spotify_client(token_info_spotify)
    
    tracks = spotify_client.get_tracks_in_playlist(playlist_id)
    
    playlist = Playlist(name=playlist_name)
    db.session.add(playlist)
    
    for track in tracks:
        song = Track(title=track.name, artist=track.artists, playlist=playlist)
        db.session.add(song)
     
        # # Create and save the token
        # token_obj = Token(token=token, playlist=playlist)
        # db.session.add(token_obj)
        
        # db.session.commit()
        # flash('Playlist and token generated successfully!')
    return "sa"


@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/auth_spotify')
def auth_spotify():
    print("TUK")
    spotify_client = get_spotify_client(session_token_info=None)
    auth_url = spotify_client.login()
    print(auth_url)
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
        session[TOKEN_INFO_DEEZER] = access_token
        return redirect(url_for('playlists'))
    else:
        return "Failed to retrieve access token."
    
    
@app.route('/redirect')
def redirect_page():
    code = request.args.get('code')
    spotify_client = get_spotify_client(session_token_info=None)
    token_info = spotify_client.exchange_code_for_token(code)
    print("BROOOOOO")
    if token_info:
        print("AAAAAA")
        spotify_client = get_spotify_client(session_token_info=token_info)
        user = spotify_client.get_current_user()
        print(user.email)
        user_db = User.query.filter_by(email=user.email).first()
        print(user_db.email)
        if user_db is None:
            user_db = User(email=user.email, display_name=user.display_name, id=user.id)
            db.session.add(user_db)
            db.session.commit()
        
        login_user(user_db)
        
        session[TOKEN_INFO_SPOTIFY] = token_info
        return redirect(url_for('playlists'))
    else:
        return "Failed to retrieve access token."

@app.route('/test', methods=['GET'])
def test():
    # logout_user()

    return str(current_user.is_authenticated)


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    form_name = request.form['form_name']
    new_playlist_name = request.form['new_playlist_name']
    playlist_id = None
    trasfer_url = None
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
            'artists': track.artists,
            'uri' : track.uri,
            'image_url': track.image_url
        }
    return jsonify(data=serialized_data), 200

@app.route('/logout')
def logout():
    # Clear the authentication tokens from the session when the user logs out
    session.pop(TOKEN_INFO_SPOTIFY, None)
    session.pop(TOKEN_INFO_DEEZER, None)
    logout_user()
    return redirect(url_for('login'))


@app.route('/profile')
# @requires_auth
@login_required
def profile():
    
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    spotify_client = get_spotify_client(session_token_info=token_info_spotify)
    artists, genres_list = spotify_client.get_current_user_top_artists_genres()
    all_genres = [genre for sublist in genres_list for genre in sublist]
    # Count the occurrences of each genre
    genre_counts = Counter(all_genres)

    # Find the top 5 most common genres
    top_3_genres = genre_counts.most_common(5)
    return render_template('profile.html', artists=artists, genres=top_3_genres)


@app.route('/recommendations')
@login_required
def recommendations():
    check_for_expired_tokens()
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
  
    deezer_client = get_deezer_client(token_info_deezer)
    dz_tracks = deezer_client.get_current_user_recommended_tracks()

    spotify_client = get_spotify_client(token_info_spotify)
    sp_tracks = spotify_client.get_current_user_recommended_tracks()
    
    
    
    return render_template("recommendations.html", sp_tracks=sp_tracks, dz_tracks=dz_tracks)


@app.route('/playlists')
@login_required
def playlists():
    print(session.get(TOKEN_INFO_DEEZER))
    check_for_expired_tokens()
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    spotify_playlists = None
    deezer_playlists = None
    
    # print("IN HERE")
    # print(token_info_deezer)
    # now = int(time.time())
    # is_expired = int(token_info_deezer.split("expires=")[1]) - now < 60
    # print(token_info_deezer)
    # print(is_expired)
    
    if token_info_deezer:
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        deezer_playlists = deezer_client.get_playlists_curr_user()
    if token_info_spotify:
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        spotify_playlists = spotify_client.get_playlists_for_current_user()
        
    return render_template('playlists.html', spotify_playlists=spotify_playlists, deezer_playlists=deezer_playlists)

@app.route('/view/<playlist_id>/<platform>', methods=['GET'])
def view(playlist_id, platform):
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

    return render_template("playlistView.html", tracks=tracks, playlist_id=playlist_id, platform=platform.lower())


@app.route('/delete/<platform>/<playlist_id>', methods=['POST', 'GET'])
def delete(platform, playlist_id):
    print("AAAAAAAAAA")
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)

    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(session_token_info=token_info_spotify)
        spotify_client.unfollow_playlist(playlist_id=playlist_id)
    elif platform.lower() == "deezer":
        deezer_client = get_deezer_client(session_token_info=token_info_deezer)
        deezer_client.delete_playlist(playlist_id=playlist_id)

    return '', 200
    
# @app.route('/view/<playlist_id>/<platform>/search', methods=['POST'])
# def search_for_song(playlist_id, platform):
#     word = request.form["searchBar"]
    
#     token_info_deezer = session.get(TOKEN_INFO_DEEZER)
#     token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    
#     found_tracks = []
    
#     if platform.lower() == "spotify":
#         spotify_client = get_spotify_client(access_token=token_info_spotify)
#         found_tracks = spotify_client.search_for_tracks_by_name(word)
#       #TODO  search by methods!!!
#     elif platform.lower() == "deezer":
#         deezer_client = get_deezer_client(access_token=token_info_deezer)
#         # found_tracks = deezer_client.find_tracks_by_names(word)
    
#     # print("9" * 100)
#     search_results_html = render_template('playlistView.html', found_tracks=found_tracks)
#     return jsonify({'search_results_html': search_results_html})
    # for t in found_tracks:
    #     print(t.name)
    # return redirect(url_for('view', platform=platform, playlist_id=playlist_id, found_tracks=found_tracks))
    
@app.route('/search_tracks', methods=['POST'])
def search():
    # Assuming you perform a search and get search results here
    search_results = ["Result 1", "Result 2", "Result 3"]
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
            'artists': track.artists,
            'uri' : track.uri,
            'image_url': track.image_url
        }
        for track in found_tracks
    ]
    print(search_query)
    # Return the search results as JSON
    return jsonify(results=serialized_results)
    # search_query = request.form.get('searchQuery')
    # # word = request.form["searchBar"]
    # token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    # found_tracks = []

    # if platform.lower() == "spotify":
    #     spotify_client = get_spotify_client(access_token=token_info_spotify)
    #     found_tracks = spotify_client.search_for_tracks_by_name(search_query)

    # # Render the search results HTML template and return it as JSON
    # return render_template('search_results.html', found_tracks=found_tracks)

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
        'view_url': url_for('view', playlist_id=playlist.id, platform='spotify'),
        'delete_url': url_for('delete', platform='spotify', playlist_id=playlist.id),
        'platform' : 'spotify'
    }
    return jsonify(data=data), 200


@app.route('/transfer_playlist_spotify_to_deezer', methods=['POST'])
def transfer_playlist_spotify_to_deezer():
    # print("AAAAAAAAA")
    # print(request.json())
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
        'view_url': url_for('view', playlist_id=playlist.id, platform='deezer'),
        'delete_url': url_for('delete', platform='deezer', playlist_id=playlist.id),
        'platform' : 'deezer'
    }
    return jsonify(data=data), 200
    


if __name__ == '__main__':
    app.config['SESSION_COOKIE_NAME'] = 'Cookie'
    app.secret_key = 'YOUR_SECRET_KEY1'
    app.run(debug=True)
