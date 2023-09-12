from collections import Counter
import time
import requests
import json

from model.album import Album
from model.playlist import Playlist
from model.track import Track
from model.user import User
from model.artist import Artist

class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri, session_token_info=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session_token_info = session_token_info
        self.SPOTIFY_API_BASE_URL = 'https://api.spotify.com/v1/'
        self.SPOTIPY_SCOPE = "user-library-read playlist-modify-public playlist-modify-private user-top-read user-read-email user-read-private"
        self.SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
        self.SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'        
    
    def _get_headers(self):
        print(self.session_token_info)
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

    def convert_to_track(self, track_json):
        print("9" * 1000)
        print(track_json)
        print("9" * 1000)
        
        track_name = track_json["name"]
        artists = track_json["artists"]
        image_url = track_json["album"]["images"][0]["url"] if track_json["album"]["images"] else "https://e-cdns-images.dzcdn.net/images/cover//500x500-000000-80-0-0.jpg"
        uri = track_json["uri"]
        id = track_json["id"]
        album_id = track_json["album"]["id"]
        album_name = track_json["album"]["name"]
        album = Album(id=album_id, name=album_name)
        artists_list = []
        print("7" * 1000)
        for a in artists:
            name = a["name"]
            new_artist = Artist(name=name)
            artists_list.append(new_artist)
        return Track(id=id, name=track_name,uri=uri, image_url=image_url, album=album, artists=artists_list)
    
    
    def convert_to_playlist(self, playlist_json):
        id = playlist_json["id"]
        image_url = playlist_json["images"][0]["url"] if playlist_json["images"] else "https://e-cdns-images.dzcdn.net/images/cover//500x500-000000-80-0-0.jpg"
        name = playlist_json["name"]
        nb_of_tracks = playlist_json["tracks"]["total"]
        
        return Playlist(id=id, name=name, number_of_tracks=nb_of_tracks, image_url=image_url)
    
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
                playlist = self.convert_to_playlist(item)
                playlists.append(playlist)

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
                single_track = track["track"]
                print(single_track)
                new_track = self.convert_to_track(single_track)
                tracks.append(new_track)
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
    
    def get_playlist(self, playlist_id):
        headers = self._get_headers()
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            playlist_data = response.json()
            playlist = self.convert_to_playlist(playlist_data)
            return playlist
    
    def get_track(self, track_uri):
        track_id = track_uri.split(":")[2]
        url = f"{self.SPOTIFY_API_BASE_URL}tracks/{track_id}"
        headers = self._get_headers()
        
        response = requests.get(url, headers=headers)
        # print(response.text)
        if response.status_code == 200:
            track_data = response.json()
            new_track = self.convert_to_track(track_data)
            return new_track
        else:
            print(f"Error whole getting track data {response.status_code}")
        
    def search_track(self, name, artists_names):
        headers = self._get_headers()
        str_artists = ",".join(artists_names)

        url = f"{self.SPOTIFY_API_BASE_URL}search?q={name}artist:{str_artists}&type=track&offset=0&limit=5"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            songs_data = response.json()
            tracks = songs_data.get("tracks", {}).get("items", [])
            for track in tracks:
                track_name = track["name"]
                if track_name.lower().strip() in name.lower().strip() or name.lower().strip() in track_name.lower().strip():
                    uri = track["uri"]
                    return uri

    
    def get_tracks_uri(self, tracks):
        track_uris = []
        for track in tracks:
            name = track.name
            artists = track.artists
            track_uri = self.search_track(name=name, artists_names=artists)
            if track_uri and track_uri not in track_uris:
                track_uris.append(track_uri)
        return track_uris
        
    
    def add_tracks_to_playlist(self, tracks, playlist_id):
        headers = self._get_headers()
        
        track_uris = self.get_tracks_uri(tracks)
        print(track_uris)
        data = {
            "uris": list(track_uris),
            "position": 0
        }
        if len(track_uris) == 1:
            data = {
            "uris": [track_uris[0]],
            "position": 0
        }
        
    
        url = f"{self.SPOTIFY_API_BASE_URL}playlists/{playlist_id}/tracks?"
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 201:
            print("Successfully added to playlist!")
        else:
            print(response.status_code)
            print(response.text)
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
                        new_track = self.convert_to_track(track)
                        tracks.append(new_track)
                        break
        return tracks
    
    def search_for_tracks_with_name(self, name):
        found_tracks = []
        
        headers = self._get_headers()
        url = f"{self.SPOTIFY_API_BASE_URL}search?q={name}&type=track&offset=0&limit=10"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            songs_data = response.json()
            tracks = songs_data.get("tracks", {}).get("items", [])
            for track in tracks:
                new_track = self.convert_to_track(track)
                found_tracks.append(new_track)
        
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
    
    
    def get_current_user_recommended_tracks(self):
        headers = self._get_headers()
        tracks = []
        url = f"{self.SPOTIFY_API_BASE_URL}recommendations"
        artists, genres_list = self.get_current_user_top_artists_genres()
        all_genres = [genre for sublist in genres_list for genre in sublist]
        # Count the occurrences of each genre
        genre_counts = Counter(all_genres)

        # Find the top 5 most common genres
        top_5_genres = genre_counts.most_common(5)
        artists_ids = []
        for a in artists[:4]:
            artists_ids.append(a.id)
        str_artists = ",".join(artists_ids)
        
        res_genres = []
        print(top_5_genres)
        for g in top_5_genres:
            res_genres.append(g[0])
        
        str_genres = ",".join(res_genres)
        data = {
            'limit': 10,
            'seed_artists': str_artists,
            'seed_genres': str_genres,
            'seed_tracks':'0c6xIDDpzE81m2q797ordA'
        }
        print(str_artists)
        print(str_genres)
        
        url = f"{self.SPOTIFY_API_BASE_URL}recommendations?seed_artists:{str_artists}&seed_genres={str_genres}&limit=10"
        response = requests.get(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            tracks_data = response.json()
            for track in tracks_data["tracks"]:
                new_track = self.convert_to_track(track)
                tracks.append(new_track)
            return tracks
        
    def get_current_user(self):
        headers = self._get_headers()
        
        url = f"{self.SPOTIFY_API_BASE_URL}me"
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            me_data = response.json()
            display_name = me_data["display_name"]
            email = me_data["email"]
            id = me_data["id"]
            return User(display_name=display_name, id=id, email=email)
            
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
    
    
    # def get_current_user(self):
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
        # pass
    
    def refresh_token_if_needed(self):
        token_info = self.session_token_info
        print(token_info)
        now = int(time.time())
        is_expired = int(token_info['expires_in']) - now < 60

        if is_expired:
            refresh_token_info = self.refresh_token(token_info['refresh_token'])
            token_info['access_token'] = refresh_token_info['access_token']
            token_info['expires_in'] = now + refresh_token_info['expires_in']
    
        return token_info
    
    def refresh_token(self, refresh_token):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        response = requests.post(self.SPOTIFY_TOKEN_URL, data=data)
        return response.json()
    
    def get_current_user_top_artists_genres(self):
        t = "artists"
        headers = self._get_headers()
        url = f"{self.SPOTIFY_API_BASE_URL}me/top/{t}"
        response = requests.get(url, headers=headers)
        artists = []
        genres = [] 
        if response.status_code == 200:
            artists_data = response.json()
            for item in artists_data["items"]:
                id = item["id"]
                name = item["name"]
                uri = item["uri"]
                artists.append(Artist(id=id, name=name, uri=uri))
                genres.append(item["genres"])
        
        return artists, genres
    
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