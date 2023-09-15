import requests
from requests_oauthlib import OAuth2Session
from model.user import User
from model.album import Album
from model.artist import Artist
from model.playlist import Playlist
from model.track import Track
from datetime import datetime, timedelta

class DeezerClient:
    def __init__(self, app_id, client_secret, redirect_uri, session_token_info=None):
        self.app_id = app_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.session_token_info = session_token_info
        print("CONSTRCUTOE")
        print(session_token_info)
    
    def get_session_access_token(self):
        return self.session_token_info
    
    def is_token_expired(self):
        expires_in_seconds = int(self.session_token_info.split("expires=")[1])
        expiration_time = datetime.now() + timedelta(seconds=expires_in_seconds)
        current_time = datetime.now()

        # Check if the token is expired
        if current_time >= expiration_time:
            print("Access token has expired")
        else:
            print("Access token is still valid")
            
        return current_time >= expiration_time
        
    def convert_to_playlist(self, playlist_json):
        id = playlist_json["id"]
        name = playlist_json["title"]
        img = playlist_json["picture_big"]
        number_of_tracks = playlist_json["nb_tracks"]
        
        return Playlist(id=id, name=name, number_of_tracks=number_of_tracks, image_url=img)
    
    def convert_to_track(self, track_json):
        artist_id = track_json["artist"]["id"]
        artist_name = track_json["artist"]["name"]
        artist_uri = None
        artist = Artist(id=artist_id, name=artist_name, uri=artist_uri)
        
        album_name = track_json["album"]["title"]
        album_id = track_json["album"]["id"]
        
        album = Album(id=album_id, name=album_name)
        
        track_name = track_json["title"]
        id = track_json["id"]
        img = track_json["album"]["cover_big"]
        return Track(id=id, name=track_name, uri=None, image_url=img, album=album, artists=[artist])
    
    def get_current_user_recommended_tracks(self):
        url = f"https://api.deezer.com/user/me/recommendations/tracks?{self.get_session_access_token()}"
        response = requests.get(url)
        tracks = []
        print(response.text)
        if response.status_code == 200:
            tracks_data = response.json()
            for t in tracks_data["data"]:
                new_track = self.convert_to_track(t)
                tracks.append(new_track)    
        
        return tracks

    def get_current_user(self):
        url = f"https://api.deezer.com/user/me?{self.get_session_access_token()}"
        response = requests.get(url)
        
        me_data = response.json()
        display_name = me_data["name"]
        id = me_data["id"]
        email = me_data["email"]
        return User(display_name=display_name, id=id, email=email)
    
    def authorization_url(self):
        authorization_base_url = 'https://connect.deezer.com/oauth/auth.php'
        authorization_base_url = 'https://connect.deezer.com/oauth/auth.php'
        deezer = OAuth2Session(self.app_id, redirect_uri=self.redirect_uri, scope=['basic_access', 'email', 'manage_library', 'delete_library'])
        authorization_url, _ = deezer.authorization_url(authorization_base_url, ['basic_access', 'email', 'manage_library', 'delete_library'])
        return authorization_url
        # return f"https://connect.deezer.com/oauth/auth.php?app_id={self.app_id}&redirect_uri={self.redirect_uri}&perms=basic_access,email,manage_library,delete_library"
        # params = {
        #     'app_id': self.app_id,
        #     'redirect_uri': self.redirect_uri,  
        #     'perms': 'manage_library delete_library email',
        # }
        # deezer = OAuth2Session(self.app_id, redirect_uri=self.redirect_uri)
        # auth_url, state =  deezer.authorization_url(authorization_base_url, params)
        # return auth_url

    def fetch_token(self, code):
        token_url = 'https://connect.deezer.com/oauth/access_token.php'
        data = {
            'app_id': self.app_id,
            'secret': self.client_secret,
            'code': code,
            'scope': 'basic_access,email,manage_library,delete_library'
        }
        response = requests.post(token_url, data=data)
        print("TUKKKKKKKKKKKKK")
        print(response.text)
        if response.status_code == 200:
            return response.text
        return None

    def get_playlists_curr_user(self):
        print(f"BBBBBB P{self.get_session_access_token()}")
        url = f"https://api.deezer.com/user/me/playlists?{self.get_session_access_token()}"
        response = requests.get(url)
        playlists = []
        if response.status_code == 200:
            playlists_data = response.json()
            for playlist in playlists_data["data"]:
                new_playlist = self.convert_to_playlist(playlist)
                playlists.append(new_playlist)
            return playlists
        else:
            print(f"Request for getting playlists failed with status code: {response.status_code}")
        
        
    def get_tracks_in_playlist(self, playlist_id): #TODO fix track return
        response = requests.get(f"https://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}")
        tracks = []
        if response.status_code == 200:
            tracks_data = response.json()
            # print(tracks_data)
            for t in tracks_data["data"]:
                new_track = self.convert_to_track(t)
                tracks.append(new_track)
        else:
            print('Error in get tracks')
        
        return tracks

    def get_user_id(self):
        response = requests.get(f'https://api.deezer.com/user/me?{self.get_session_access_token()}')
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data['id']
            # config["user_id"] = user_id
            # print(f"User ID: {user_id}")
            return user_id
        else:
            print(f"Request failed with status code: {response.status_code}")
        
    def create_playlist(self, name):
        url = f"https://api.deezer.com/user/me/playlists?{self.get_session_access_token()}"
        response = requests.post(url, data={"title": name})  

        if response.status_code == 200:
            playlist_data = response.json()
            playlist_id = playlist_data.get("id")
            return playlist_id
        else:
            print("Failed to create playlist")
    
    def delete_playlist(self, playlist_id):
        url = f"https://api.deezer.com/playlist/{playlist_id}?{self.get_session_access_token()}"
        
        response = requests.delete(url)
        
        print("deleting playlist")
        print(response.status_code)
    
    # def add_tracks_to_playlist(self, playlist_id, tracks):
    #     track_ids = []
    #     for t in tracks:
    #         name = t.name
    #         artists = t.artists
    #         print(name)
    #         print(artists)
    #         id = self.search_track(name=str(name), artists_names=artists)
    #         track_ids.append(id)
      
    #     # data = {
    #     #     "uris": list(track_uris),
    #     #     "position": 0
    #     # }
    #     url = ""
    #     if len(track_ids) > 1:
    #         url = f"http://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}&songs={list(track_ids)}"
    #     else:
    #         url = f"http://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}&songs={track_ids[0]}"
    #     # url = f"http://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}"
    #     response = requests.post(url)
    #     print(response.status_code)
    #     print(response.text)
    #     if response.status_code == 200:
    #         print(f"Added track to the playlist")
    #     else:
    #         print(f"Failed to add track to the playlist")
    def add_tracks_to_playlist(self, playlist_id, tracks):
        track_ids = self.get_track_ids(tracks)
        print(track_ids)
        if not track_ids:
            print("No track IDs found.")
            return
        url = ""
        
        data = {
            "songs": ','.join(map(str, track_ids))
        }

        # self.add_track_id_to_playlist(track_id, playlist_id)
        url = f"http://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}"
        # if len(track_ids) == 1:
        #     data = {
        #         "songs": track_ids[0]
        #     }
        # data = {"songs": track_ids, "order": track_ids}
        
        response = requests.post(url, data=data)
        print(response.text)
        if response.status_code == 200:
            print(f"Added tracks to the playlist")
        else:
            print(f"Failed to add tracks to the playlist")
            print(response.text)
    
    def get_track_ids(self, tracks):
        track_ids = []
        for track in tracks:
            name = track.name
            artists = track.artists
            artists_names = [artist.name for artist in artists]
            track_id = self.search_track(name=name, artists_names=artists_names)
            if track_id and track_id not in track_ids:
                track_ids.append(track_id)
        return track_ids
    
    def add_track_id_to_playlist(self, playlist_id, track_id):
    
        url = f"http://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}&songs={track_id}"
        # url = f"http://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}"
        
        response = requests.post(url)
        print(response.text)
        print(response.status_code)
        if response.status_code == 200:
            print(f"Added track to the playlist")
        else:
            print(f"Failed to add track to the playlist")
    
    
    def get_track(self, track_id):
        url = f"https://api.deezer.com/track/{track_id}?{self.get_session_access_token()}"
        response = requests.get(url)
        if response.status_code == 200:
            track_data = response.json()
            new_track = self.convert_to_track(track_data)
            return new_track
        else:
            print(f"Error while getting track {response.status_code}")

    def remove_track_from_playlist(self, playlist_id, track_id):
        url = f"https://api.deezer.com/playlist/{playlist_id}/tracks?{self.get_session_access_token()}&songs={track_id}"
        response = requests.delete(url)
        print(response.status_code)
    
    def search_for_tracks_with_name(self, name):
        url = f"https://api.deezer.com/search/track?q={name}&{self.get_session_access_token()}"
        tracks = []
        response = requests.get(url)
        if response.status_code == 200:
            tracks_data = response.json()
            for song in tracks_data["data"]:
                new_track = self.convert_to_track(song)
                tracks.append(new_track)
        else:
            print(f"Error while fething search results: {response.status_code}")
        
        return tracks
    

    
    def get_playlist_info(self, playlist_id):
        print(playlist_id)
        url = f"https://api.deezer.com/playlist/{playlist_id}?{self.get_session_access_token()}"
        response = requests.get(url)
        print(response.text)
        if response.status_code == 200:
            playlist_data = response.json()
            playlist = self.convert_to_playlist(playlist_data)
            return playlist
        else:
            print(f"Error while fething search results: {response.status_code}")

    # def find_track_by_name_artist(self, name, artists_names):
    #     str_artists = ""
    #     print(f"str_artists: {str_artists}")
        
    #     for b in artists_names:
    #         str_artists += ","
    #         str_artists += b
            
            
    #     endpoint = f"https://api.deezer.com/search/track?q={str_artists}-{name}"
    #     response = requests.get(endpoint)
    #     print(endpoint)
    #     print(response.text)
    #     if response.status_code == 200:
    #         song_data = response.json()
    #         if song_data["data"] == []:
    #             splited = name.split("-")
    #             new_name = splited[0]
    #             endpoint = f"https://api.deezer.com/search/track?q={new_name}"
    #             print(endpoint)
    #             response = requests.get(endpoint)
    #             if response.status_code == 200:
    #                 song_data = response.json()
    #                 for song in song_data["data"]:
    #                     title = song["title"]
    #                     print(new_name)
    #                     print(title.lower())
    #                     print(new_name.lower().strip() in title.lower().strip())
    #                     if new_name.lower().strip() in title.lower().strip():
    #                         song_id = song["id"]
    #                         print(f"Id = {song_id}")
    #                         return song_id
    #         else:
    #             for song in song_data["data"]:
    #                 title = song["title"]
    #                 print(name)
    #                 print(title.lower())
    #                 print(name.lower() in title.lower())
    #                 if name.lower() in title.lower():
    #                     song_id = song["id"]
    #                     print(f"Id = {song_id}")
    #                     return song_id
    #     else:
    #         print(f"Failed to find track with name {name}")
        
    def search_track(self, name, artists_names):
        str_artists = ",".join(artists_names)
        print(f"Searching for track: {name} by {str_artists}")
        
        song_id = self._search_track_by_name_and_artists(name, artists_names)
        
        if not song_id:
            print(f"Failed to find track with name {name} by {str_artists}")
        
        return song_id
    
    @staticmethod
    def _compare_names(name1, name2):
        return name2.lower().strip() in name1.lower().strip()
    
    def _search_track_by_name_and_artists(self, name, artists_names):
        endpoint = f"https://api.deezer.com/search/track?q={artists_names}-{name}"
        response = requests.get(endpoint)
        print(endpoint)

        if response.status_code == 200:
            song_data = response.json()
            for song in song_data["data"]:
                title = song["title"]
                if self._compare_names(name, title):
                    song_id = song["id"]
                    print(f"Found track with name {name} by {artists_names}. Id = {song_id}")
                    return song_id

        return self._search_track_by_name(name, artists_names)

    def _search_track_by_name(self, name, artists_names):
        str_artists = ",".join(artists_names)
        endpoint = f"https://api.deezer.com/search/track?q={name}-{str_artists}"
        response = requests.get(endpoint)
        print("_search_track_by_name")
        if response.status_code == 200:
            song_data = response.json()
            for song in song_data["data"]:
                title = song["title"]
                if self._compare_names(name, title):
                    song_id = song["id"]
                    print(f"Found track with name {name}. Id = {song_id}")
                    return song_id

        return self._search_track_by_splited_name(name, artists_names)
    
    def _search_track_by_splited_name(self, name, artists_names):
        print("_search_track_by_splited_name")
        splited = name.split("-")
        str_artists = ",".join(artists_names)
        endpoint = f"https://api.deezer.com/search/track?q={splited[0]}-{str_artists}"
        response = requests.get(endpoint)
        print(endpoint)
        print(response.text)
        if response.status_code == 200:
            song_data = response.json()
            for song in song_data["data"]:
                title = song["title"]
                print(self._compare_names(name, title))
                if self._compare_names(name, title):
                    song_id = song["id"]
                    print(f"Found track with name {name}. Id = {song_id}")
                    return song_id

        return self._search_track_by_splited_spaces_name(name, artists_names)
    
    def _search_track_by_splited_spaces_name(self, name, artists_names):
        splited = name.split(" ")
        str_artists = ",".join(artists_names)
        endpoint = f"https://api.deezer.com/search/track?q={splited[0]}-{str_artists}"
        response = requests.get(endpoint)
        print(endpoint)
        print(response.text)
        if response.status_code == 200:
            song_data = response.json()
            for song in song_data["data"]:
                title = song["title"]
                print(self._compare_names(name, title))
                if self._compare_names(name, title):
                    song_id = song["id"]
                    print(f"Found track with name {name}. Id = {song_id}")
                    return song_id

        return None
    
    def _search_track_by_name_and_artists(self, name, artists_names):
        endpoint = f"https://api.deezer.com/search/track?q={artists_names}-{name}"
        response = requests.get(endpoint)
        print(endpoint)
        print("_search_track_by_name_and_artists")

        if response.status_code == 200:
            song_data = response.json()
            for song in song_data["data"]:
                title = song["title"]
                if self._compare_names(name, title):
                    song_id = song["id"]
                    print(f"Found track with name {name} by {artists_names}. Id = {song_id}")
                    return song_id

        return self._search_track_by_name(name, artists_names)
#     def get_tracks(playlist_id, access_token):
#     artist_song_dict = {}
#     tracks = requests.get(f"https://api.deezer.com/playlist/{playlist_id}/tracks?access_token={access_token}")
    
#     if tracks.status_code == 200:
#         tracks_data = tracks.json()
#         for t in tracks_data["data"]:
#             artist_name = t["artist"]["name"]
#             track_name = t["title"]
#             artist_song_dict[artist_name][track_name]
#     else:
#         print('Error in get tracks')
    
#     return artist_song_dict
    
# def get_playlists_curr_user(access_token):
#     a = f"https://api.deezer.com/user/me/playlists?access_token={access_token}"
#     response = requests.get(a)
#     d = []
#     if response.status_code == 200:
#         playlists_data = response.json()
#         for playlist in playlists_data["data"]:
#             title = playlist["title"]
#             picture = playlist["picture_small"]
#             number_of_tracks = playlist["nb_tracks"]
#             d.append({"title": title, "picture": picture, "number_of_tracks": number_of_tracks}) 
#         return d
#     else:
#         print(f"Request for getting playlists failed with status code: {response.status_code}")
    
# def get_user(access_token):
#     response = requests.get(f'https://api.deezer.com/user/me?access_token={access_token}')
#     if response.status_code == 200:
#         user_data = response.json()
#         user_id = user_data['id']
#         config["user_id"] = user_id
#         print(f"User ID: {user_id}")
#         return user_id
#     else:
#         print(f"Request failed with status code: {response.status_code}")
    

# def create_playlist(access_token, title):
#     api_endpoint = f"https://api.deezer.com/user/me/playlists?access_token={access_token}"
#     response = requests.post(api_endpoint, data={"title": title})  
#     print(response.text) 
#     print(response.status_code)
#     if response.status_code == 200:
#         playlist_data = response.json()
#         playlist_id = playlist_data.get("id")
#         print(f"Created playlist with ID: {playlist_id}")
#         return playlist_id
#     else:
#         print("Failed to create playlist")
        
# def add_to_playlist(access_token, playlist_id, track_ids):

#     for track_id in track_ids:
#         add_track_endpoint = f"http://api.deezer.com/playlist/{playlist_id}/tracks?access_token={access_token}&songs={track_id}"
#         response = requests.post(add_track_endpoint)
#         if response.status_code == 200:
#             print(f"Added track with ID {track_id} to the playlist")
#         else:
#             print(f"Failed to add track with ID {track_id} to the playlist")
    
# def find_songs_by_names(names):
#     ids = []
#     for track in names:
#         for artist_name, track_name in track.items():
#             print(f"{artist_name}-{track_name}")
#             # track_name = track_name.replace(" ", "_")
#             # artist_name = artist_name.replace(" ", "_")
#             endpoint = f"https://api.deezer.com/search/track?q={artist_name}-{track_name}"
#             response = requests.get(endpoint)
#             if response.status_code == 200:
#                 song_data = response.json()
#                 for song in song_data["data"]:
#                     title = song["title"]
#                     if track_name.lower() in title.lower():
#                         song_id = song["id"]
#                         ids.append(song_id)
#                         print(f"Found song with ID {song_id} and name {track_name}")
#                         break
#             else:
#                 print(f"Failed to find track with name {track_name}")
    
#     return ids