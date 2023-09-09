import time
import requests
import json
from .playlist import Playlist
from .track import Track

class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri, session_token_info=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session_token_info = session_token_info
        self.SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1/'
        self.SPOTIPY_SCOPE = "user-library-read playlist-modify-public playlist-modify-private user-top-read"
        self.SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
        self.SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'        
    
    def _get_headers(self):
        access_token = self.session_token_info['access_token']
        headers = {"Authorization": f"Bearer {access_token}"}
        return headers

    def _exchange_code_for_token(self, code):
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(f'{self.SPOTIFY_TOKEN_URL}', data=data)
        return response.json()

    def login(self):
        auth_url = f"{self.SPOTIFY_AUTH_URL}?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&scope={self.SPOTIPY_SCOPE}"
        return auth_url

    def exchange_code_for_token(self, code):
        token_info = self._exchange_code_for_token(code)
        self.session_token_info = token_info
        return token_info

    def get_playlists_for_current_user(self):
        headers = self._get_headers()
        url = f"{self.SPOTIFY_API_BASE_URL}me/playlists"
        
            #TODO: params
            # params = {
            #     "limit": 100,
            #     "offset": 5
            # }
        result = requests.get(url=url, headers=headers)
        playlists = []

        if result.status_code == 200:
            playlists_data = result.json()
            for item in playlists_data["items"]:
                id = item["id"]
                image_url = item["images"][0]["url"] if item["images"] else "https://e-cdns-images.dzcdn.net/images/cover//500x500-000000-80-0-0.jpg"
                name = item["name"]
                nb_of_tracks = item["tracks"]["total"]
                playlists.append(Playlist(id, image_url, name, nb_of_tracks))
                # playlists[id] = {"image_url": image_url, "name": name, "number_of_tracks": nb_of_tracks}

        return playlists
    
    # no delete in spotify api
    def unfollow_playlist(self, playlist_id):
        headers = self._get_headers()
        # user_id = self.get_current_user_id()
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}/followers"
        
        response = requests.delete(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            print("Spotify playlist deleted successfully!")
        else:
            print(f"Error while deleting playlist with status code: {response.status_code}")
        pass
    
    def get_tracks_in_playlist(self, playlist_id, limit=100, offset=0):
        headers = self._get_headers()
        params = {
            "fields": "items(track(name, artists(name), uri, album, id))",
            "limit": limit,
            "offset": offset
        }
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}/tracks"
        response = requests.get(url=url, params=params, headers=headers)

        tracks = []
        if response.status_code == 200:
            tracks_data = response.json()
            for track in tracks_data["items"]:
                track_name = track["track"]["name"]
                artists = track["track"]["artists"]
                artist_names = [artist["name"] for artist in artists]
                small_image_url = track["track"]["album"]["images"][0]["url"] if track["track"]["album"]["images"] else None
                uri = track["track"]["uri"]
                id = track["track"]["id"]
                tracks.append(Track(uri=uri, name=track_name, artists=artist_names, small_image_url=small_image_url, id=id))
            return tracks
    
    def get_current_user_id(self):
        headers = self._get_headers()
        response = requests.get(f"{self.SPOTIFY_API_BASE_URL}me", headers=headers)
        return response.json()['id']
    
    def create_playlist(self, name):
        headers = self._get_headers()
        user_id = self.get_current_user_id()
        url = f"{self.SPOTIFY_API_BASE_URL}users/{user_id}/playlists"
        data = {
            "name": name,
            "description": "New playlist description",
            "public": True
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 201:
            print("Playlist created maybe :)")
            return response.json()["id"]
        else:
            print(f"Errr while creating playlist with status code: {response.status_code}")
    
    
    def add_track_uri_to_playlist(self, track_uri, playlist_id):
        headers = self._get_headers()
        print(track_uri)
        data = {
            "uris": [track_uri],
            "position": 0
        }
    
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}/tracks?"
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        print(response.text)
        if response.status_code == 201:
            print("Successfully added to playlist!")
        else:
            print(response.status_code)
            print("Err while adding tracks to playlist!")
    
    
    def get_track(self, track_uri):
        track_id = track_uri.split(":")[2]
        url = f"{self.SPOTIFY_API_BASE_URL}tracks/{track_id}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        # print(response.text)
        if response.status_code == 200:
            track_data = response.json()
            id = track_data["id"]
            name = track_data["name"]
            artists_names = []
            for artist in track_data["artists"]:
                artists_names.append(artist["name"])
            uri = track_data["uri"]
            small_image_url = track_data["album"]["images"][-1]["url"]
            return Track(id=id, name=name, artists=artists_names, uri=uri, small_image_url=small_image_url)
        else:
            print(f"Error whole getting track data {response.status_code}")
            
    
    def add_tracks_to_playlist(self, tracks, playlist_id):
        headers = self._get_headers()
        track_uris = [track.uri for track in tracks]
      
        data = {
            "uris": list(track_uris),
            "position": 0
        }
    
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}/tracks?"
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 201:
            print("Successfully added to playlist!")
        else:
            print(response.status_code)
            print("Err while adding tracks to playlist!")
            
    def find_tracks_by_names(self, names):
        headers = self._get_headers()
        tracks = []
        
        for name in names:
            url = f"{self.SPOTIFY_API_BASE_URL}search?q={name}&type=track&offset=0&limit=5"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                songs_data = response.json()
                tracks = songs_data.get("tracks", {}).get("items", [])
                for track in tracks:
                    track_name = track["name"]
                    if track_name.lower() in name.lower():
                        artists_names = []
                        for artist in track["artists"]:
                            artists_names.append(artist["name"])
                        uri = track["uri"]
                        id = track["id"]
                        small_image_url = track["album"]["images"][-1]["url"]
                        tracks.append(Track(name=track_name, artists=artists_names, uri=uri, small_image_url=small_image_url, id=id))
                        break
        return tracks
    
    def search_for_tracks_with_name(self, name):
        found_tracks = []
        
        headers = self._get_headers()
        url = f"{self.SPOTIFY_API_BASE_URL}search?q={name}&type=track&offset=0&limit=10"

        response = requests.get(url, headers=headers)
        print(f"response: {response.status_code}")
        if response.status_code == 200:
            songs_data = response.json()
            tracks = songs_data.get("tracks", {}).get("items", [])
            for track in tracks:
                print(track)
                print("9" * 1000)
                track_name = track["name"]
                artists_names = []
                for artist in track["artists"]:
                    artists_names.append(artist["name"])
                uri = track["uri"]
                id = track["id"]
                small_image_url = track["album"]["images"][-1]["url"]
                found_tracks.append(Track(name=track_name, artists=artists_names, uri=uri, small_image_url=small_image_url, id=id))
        
        return found_tracks
    
    def remove_track_from_playlist(self, track_uri, playlist_id):
        headers = self._get_headers()
        
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}/tracks"
        print(track_uri)
        data = {
                "tracks": [
                {
                    "uri": track_uri
                }
            ]
        }
        
        response = requests.delete(url, headers=headers, data=json.dumps(data))
        print(response.text)
        if response.status_code == 200:
            print("Successfully removed track from playlist!")
        else:
            print(f"Error: {response.status_code} while removing track from playlist!")
    
    def get_current_user(self):
        # token = session[TOKEN_INFO]['access_token']
        # st = f"Bearer {token}"
        # headers = {"Authorization": st}
        
        # url = f"{self.SPOTIFY_API_BASE_URL}me"
        
        # response = requests.get(url, headers=headers)
        # '''
        #         {
        #     "country": "string",
        #     "display_name": "string",
        #     "email": "string",
        #     "explicit_content": {
        #         "filter_enabled": false,
        #         "filter_locked": false
        #     },
        #     "external_urls": {
        #         "spotify": "string"
        #     },
        #     "followers": {
        #         "href": "string",
        #         "total": 0
        #     },
        #     "href": "string",
        #     "id": "string",
        #     "images": [
        #         {
        #         "url": "https://i.scdn.co/image/ab67616d00001e02ff9ca10b55ce82ae553c8228",
        #         "height": 300,
        #         "width": 300
        #         }
        #     ],
        #     "product": "string",
        #     "type": "string",
        #     "uri": "string"
        #     }
        
        # '''
        
        # if response.status_code == 200: 
        #     print("Successfully fetched current user information!")
        #     return response.json()
        # else:
        #     print("Error while fetching current user information!")
        pass
    
    
    # def get_token(self,):
    #     token_info = self.session_token_info
    #     if not token_info:
    #         redirect(url_for('login', _external=False))
        
    #     now = int(time.time())
    #     is_expired = token_info['expires_at'] - now < 60

    #     if is_expired:
    #         refresh_token_info = refresh_token(token_info['refresh_token'])
    #         token_info['access_token'] = refresh_token_info['access_token']
    #         token_info['expires_at'] = now + refresh_token_info['expires_in']
    
    #     return token_info
    
    # def refresh_token(refresh_token):
    #     data = {
    #         'grant_type': 'refresh_token',
    #         'refresh_token': refresh_token,
    #         'client_id': CLIENT_ID,
    #         'client_secret': CLIENT_SECRET,
    #     }
    #     response = requests.post(SPOTIFY_TOKEN_URL, data=data)
    #     return response.json()