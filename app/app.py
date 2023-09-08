from flask import Flask, request, url_for, session, redirect, render_template, jsonify
import os
from model.spotify_client import SpotifyClient
from model.deezer_client import DeezerClient

app = Flask(__name__)

TOKEN_INFO_SPOTIFY = 'token_info_spotify'
TOKEN_INFO_DEEZER = 'token_info_deezer'

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

DEEZER_APP_ID = os.getenv("DEEZER_APP_ID")
DEEZER_CLIENT_SECRET = os.getenv("DEEZER_CLIENT_SECRET")
DEEZER_REDIRECT_URI = os.getenv("DEEZER_REDIRECT_URI")

def get_spotify_client(access_token):
    return SpotifyClient(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI, session_token_info=access_token)

def get_deezer_client(access_token):
    return DeezerClient(DEEZER_APP_ID, DEEZER_CLIENT_SECRET, DEEZER_REDIRECT_URI, session_access_token=access_token)

@app.route('/')
def login():
    return render_template("base.html")

@app.route('/auth_spotify')
def auth_spotify():
    spotify_client = get_spotify_client(access_token=None)
    auth_url = spotify_client.login()
    return redirect(auth_url)

@app.route('/auth_deezer')
def auth_deezer():
    deezer_client = get_deezer_client(access_token=None)
    auth_url = deezer_client.authorization_url()
    return redirect(auth_url)

@app.route("/callback", methods=["GET"])
def callback(): 
    code = request.args.get('code')
    deezer_client = get_deezer_client(access_token=None)
    access_token = deezer_client.fetch_token(code)
    if access_token:
        session[TOKEN_INFO_DEEZER] = access_token
        return redirect(url_for('playlists'))
    else:
        return "Failed to retrieve access token."
    
    
@app.route('/redirect')
def redirect_page():
    code = request.args.get('code')
    spotify_client = get_spotify_client(access_token=None)
    token_info = spotify_client.exchange_code_for_token(code)
    session[TOKEN_INFO_SPOTIFY] = token_info
    return redirect(url_for('playlists'))

@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    
    form_name = request.form['form_name']
    new_playlist_name = request.form['new_playlist_name']
    playlist_id = None
    if form_name.lower() == "spotify":
        spotify_client = get_spotify_client(access_token=token_info_spotify)
        playlist_id = spotify_client.create_playlist(name=new_playlist_name.strip())
    elif form_name.lower() == "deezer":
        deezer_client = get_deezer_client(access_token=token_info_deezer)
        playlist_id = deezer_client.create_playlist(name=new_playlist_name.strip())
    
    data = { 
        'playlist_id': playlist_id,
        'playlist_name': new_playlist_name,
        'view_url': url_for('view', playlist_id=playlist_id, platform='spotify'),
        'delete_url': url_for('delete', platform='spotify', playlist_id=playlist_id),
        'transfer_url': url_for('transfer_to_deezer', playlist_id=playlist_id)
    }
     
    # Return the search results as JSON
    return jsonify(data=data)
    
    return redirect(url_for('playlists'))


@app.route('/playlists')
def playlists():
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    spotify_playlists = None
    deezer_playlists = None
    
    if token_info_deezer:
        deezer_client = get_deezer_client(access_token=token_info_deezer)
        deezer_playlists = deezer_client.get_playlists_curr_user()
    if token_info_spotify:
        spotify_client = get_spotify_client(access_token=token_info_spotify)
        spotify_playlists = spotify_client.get_playlists_for_current_user()
        
    return render_template('playlists.html', spotify_playlists=spotify_playlists, deezer_playlists=deezer_playlists)

@app.route('/view/<playlist_id>/<platform>', methods=['GET'])
def view(playlist_id, platform):
    tracks = []
    print("AAAA", playlist_id)
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    
    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(access_token=token_info_spotify)
        tracks = spotify_client.get_tracks_in_playlist(playlist_id=playlist_id)
    elif platform.lower() == "deezer":
        deezer_client = get_deezer_client(access_token=token_info_deezer)
        tracks = deezer_client.get_tracks_in_playlist(playlist_id=playlist_id)

    return render_template("playlistView.html", tracks=tracks, playlist_id=playlist_id, platform=platform.lower())


@app.route('/delete/<platform>/<playlist_id>', methods=['POST', 'GET'])
def delete(platform, playlist_id):
    print("AAAAAAAAAA")
    token_info_deezer = session.get(TOKEN_INFO_DEEZER)
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)

    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(access_token=token_info_spotify)
        spotify_client.unfollow_playlist(playlist_id=playlist_id)
    elif platform.lower() == "deezer":
        deezer_client = get_deezer_client(access_token=token_info_deezer)
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
    
@app.route('/baba', methods=['POST'])
def search():
    # Assuming you perform a search and get search results here
    search_results = ["Result 1", "Result 2", "Result 3"]
    search_query = request.json.get('searchQuery')
    platform = request.json.get('platform')
    
    token_info_spotify = session.get(TOKEN_INFO_SPOTIFY)
    found_tracks = []

    if platform.lower() == "spotify":
        spotify_client = get_spotify_client(access_token=token_info_spotify)
        found_tracks = spotify_client.search_for_tracks_by_name(search_query)
    
    serialized_results = [
        {
            'id': track.id,
            'name': track.name,
            'artists': track.artists,
            'uri' : track.uri,
            'image_url': track.small_image_url
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
        spotify_client = get_spotify_client(access_token=token_info_spotify)
        spotify_client.remove_track_from_playlist(track_id, playlist_id)
    elif platform == 'deezer':
        deezer_client = get_deezer_client(access_token=token_info_deezer)
        deezer_client.remove_track_from_playlist(playlist_id=playlist_id, track_id=track_id)
    return jsonify(), 200


@app.route('/transfer_to_deezer/<playlist_id>', methods=['POST', 'GET'])
def transfer_to_deezer(playlist_id):
    
    return "blabla" + playlist_id
    


if __name__ == '__main__':
    app.config['SESSION_COOKIE_NAME'] = 'Cookie'
    app.secret_key = 'YOUR_SECRET_KEY1'
    app.run(debug=True)
