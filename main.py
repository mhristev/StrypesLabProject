import os
from flask import Flask, request, redirect, session, url_for, render_template
from dotenv import load_dotenv
import os

from model.deezer_client import DeezerClient

load_dotenv()

app = Flask(__name__)

# Configure your app here if needed
app.secret_key = "SECRET_KEY"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

# Initialize your DeezerClient with your credentials from environment variables
deezer_client = DeezerClient(
    os.getenv("DEEZER_APP_ID"),
    os.getenv("DEEZER_CLIENT_SECRET"),
    os.getenv("DEEZER_REDIRECT_URI")
)
app.config['SESSION_COOKIE_NAME'] = 'Deezer Cookie'

@app.route("/")
def index():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Deezer)
    using an URL with a few key OAuth parameters.
    """
    auth_url = deezer_client.authorization_url()
    print(auth_url)
    return redirect(auth_url)

    # deezer = OAuth2Session(config['app_id'], redirect_uri=config['redirect_uri'])
    # authorization_url, state = deezer.authorization_url(authorization_base_url)
    # print(authorization_url)
    # # State is used to prevent CSRF, keep this for later.
    # session['oauth_state'] = state
    
    # return redirect(authorization_url)

@app.route('/view/<playlist_id>', methods=['POST', 'GET'])
def view(playlist_id):
    print(playlist_id)
    tracks = deezer_client.get_tracks_in_playlist(playlist_id)

    for track in tracks:
        print(track.id)
    return render_template("playlistView.html", tracks=tracks, playlist_id=playlist_id)

@app.route('/from/<playlist_id>/remove/<track_id>', methods=['POST', 'GET'])
def remove_track_from_playlist(playlist_id, track_id):
    deezer_client.remove_track_from_playlist(playlist_id, track_id)
    return redirect(url_for("view", playlist_id=playlist_id))


@app.route('/view/<playlist_id>/search/<search_word>', methods=['POST'])
def search_for_song(playlist_id, search_word):
    return playlist_id + search_word



@app.route('/create_playlist/<new_playlist_name>', methods=['POST'])
def create_playlist(new_playlist_name):
    if request.method == 'POST':
        print("+" * 10)
        print(new_playlist_name)
        deezer_client.create_playlist(new_playlist_name)
        return redirect(url_for('profile'))
    else:
        return "Get loser"

@app.route('/delete/<playlist_id>', methods=['POST', 'GET'])
def delete(playlist_id):
    deezer_client.delete_playlist(playlist_id)
    return redirect(url_for('profile'))
# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback(): 
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    code = request.args.get('code')
    access_token = deezer_client.fetch_token(code)
    if access_token:
        session['token_info'] = access_token
        print(f"token: {access_token}")
        return redirect(url_for('profile'))
    else:
        return "Failed to retrieve access token."
    
    
    
    
    # code = request.args.get('code')
    # print(code)
   
    # # deezer = OAuth2Session(config['app_id'], state=session['oauth_state'])
    # # print(deezer)
    # # token = deezer.fetch_token(token_url,
    # #                            client_secret=config['client_secret'],
    # #                            authorization_response=request.url)
    
    # # At this point you can fetch protected resources but lets save
    # # the token and show how this is done from a persisted token
    # # in /profile.
    # # Define the token endpoint URL
    # token_url = 'https://connect.deezer.com/oauth/access_token.php'

    # # Prepare the data to send in the POST request
    # data = {
    #     'app_id': "630924",
    #     'secret': "3ad64023cadc7cf3ef9733f754770808",
    #     'code': code,
    # }

    # # Make a POST request to the token endpoint
    # response = requests.post(token_url, data=data)
    # access_token = None
    # if response.status_code == 200:
    # # Access the response content which should contain the access token
    #     access_token = response.text
    #     print(f'Access Token: {access_token}')
    # else:
    #     print(f"Request failed with status code: {response.status_code}")
    # # token_url = requests.get(f"https://connect.deezer.com/oauth/access_token.php?app_id=630924&secret=3ad64023cadc7cf3ef9733f754770808&code={code}")
    # # print(dict(parse_qsl(token_url)))
    # session['token_info'] = access_token.split("=")[1]
    # print("================================================")
    # print(access_token)
    # print("================================================")
    # return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """
    Fetching a protected resource using an OAuth 2 token.
    """
    access_token = session.get('token_info')
    if access_token:
        playlists = deezer_client.get_playlists_curr_user()
        return render_template('playlists.html', playlists=playlists)
    else:
        return "Token not found. Please authenticate first."

   
    # access_token = session.get('token_info')
    # if access_token:
    #     print(access_token)
    #     names = \
    #     [
    #         {"Mac Miller": "Love Lost"},
    #         {"Travis Scott": "TELEKINESIS"},
    #         {"Travis Scott": "LOOOVE"}
    #     ]
    #     # playlist_id = create_playlist(access_token=access_token, title="Travis Songs")
    #     # ids = find_songs_by_names(names)
    #     # add_to_playlist(access_token=access_token, playlist_id=playlist_id, track_ids=ids)

    #     playlists = get_playlists_curr_user(access_token)
    #     res = ""
    #     for p in playlists:
    #         title = p["title"]
    #         picture = p["picture"]
    #         number_of_tracks = p["number_of_tracks"]
    #         res += f"\nTitle: {title}, Picture: {picture}, Number of Tracks: {number_of_tracks}\n"
    #     return res
    # else:
    #     return "Token not found. Please authenticate first."


        
        
if __name__ == "__main__":
    app.run(debug=True)