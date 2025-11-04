import spotipy, re, os, sys
from pathlib import Path
from spotipy import Spotify
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from .common_tools import (generate_random_name, download_image, pick_best_match)
from .exceptional import ClassicException
from dotenv import load_dotenv

# Load environment variables
env_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
env_path = env_path / ".env"  
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

##------------------Real action below--------------------


class SpotifyAuth():
    def __init__(self):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
                                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                                redirect_uri=os.getenv("REDIRECT_URL"),
                                scope=os.getenv("SCOPE_STR"), open_browser=True))            

    def is_authenticated(self, spotify_obj: Spotify) -> bool:
        try:
            # Try to call any private method
            spotify_obj.current_user()
            return True
        except (SpotifyException) as e:
            if e.http_status != 200:
                return False
            raise ClassicException("UNKNOWN failure", 99)

class SpotifyBase(SpotifyAuth):
    def __init__(self):
        super().__init__()
        if not self.is_authenticated(self.spotify):
            raise ClassicException(msg='UNAUTHENTICATED BRUH, try again', err_code=90)
        self.export_playlist = []

    #auth
    def get_user_results(self):
        return self.spotify.current_user_playlists(limit=20)['items']

    #auth
    def get_playlist_id_from_title(self, playlist_title: str) -> str:
        for playlist in self.get_user_results():
            if playlist['name'] == playlist_title:
                return playlist['id']
        print(f"No playlist found with name: {playlist_title}")
        ClassicException(msg=f"No playlist found with title: {playlist_title}", err_code=10)
    
    #no-auth
    def get_playlist_id_from_external_link(self, url: str):
        regex = r".*playlist/(\S+)[\?].*"
        try: 
            playlist_id = re.match(regex, url).group(1)
            return playlist_id
        except:
            raise ClassicException("INVALID playlist URL, dumbASS!", 30)
    
    #no-auth
    def get_playlist_thumbnail(self, playlist_id: str):
        thumbnail = self.spotify.playlist_cover_image(playlist_id)
        if type(thumbnail) == list:
            return thumbnail[0]['url']
        elif (type(thumbnail) == str) and (re.match(r"http.*:.*/+.*", thumbnail)):
            return thumbnail
    
    #auth
    def set_playlist_thumbnail(self, playlist_id: str, img_url: str):
        import base64
        img = download_image(img_url)
        with open(img, "rb") as mg:
            img = base64.b64encode(mg.read()).decode()
        return self.spotify.playlist_upload_cover_image(playlist_id, img)
    
    #no-auth
    def get_all_song_ids_from_playlist(self, playlist_id: str) -> list:
        all_songs_ids = []
        playlist = self.spotify.playlist_items(playlist_id, additional_types=("track"))
        for track in playlist.get('items'):
            all_songs_ids.append(track.get('track').get('id'))
        return all_songs_ids
    
    #auth
    def create_playlist(self, random_title: bool = True, description: str = "", user_title: bool = "My Playlist #", thumbnail_url: str = ""):
        new_playlist_id = self.spotify.user_playlist_create(self.spotify.current_user()['id'], user_title if random_title is False else generate_random_name(), description=description)['id']
        if thumbnail_url != "":
            try:
                self.set_playlist_thumbnail(new_playlist_id, thumbnail_url)
            except Exception as e:
                raise ClassicException(msg=f"UNKNOWN EXCEPTION: {e}", err_code=99)
        return new_playlist_id
    
    #no-auth
    def get_song_id_from_external_link(self, url: str):
        regex = r".*track/(\S+)[\?].*"
        playlist_id = re.match(regex, url).group(1)
        return playlist_id

    #auth
    def add_songs_to_playlist(self, playlist_id: str, track_ids: list):
        if not self.spotify.playlist_add_items(playlist_id, track_ids):
            raise ClassicException(msg='ERROR adding songs to playlist', err_code=10)
        else:
            return True

    #no-auth
    def search_track(self, song_dict: dict):
        query_str = f"{song_dict['title']} {", ".join(song_dict['artists'])} {song_dict['album']}"

        results = self.spotify.search(query_str, limit=5, type='track')
        if not results:
            raise ClassicException(msg="No songs found for: " + f"{song_dict['title']} {", ".join(song_dict['artists'])}", err_code=10)
        
        track_match = pick_best_match('spotify', results['tracks']['items'], song_dict['title'], song_dict['artists'])
        print(f"Match found! \n" \
              f"Title: {track_match['name']}\n" \
              f"Artists: {[artist['name'] for artist in track_match['artists']]}\n" \
              f"Album: {track_match['album']['name']}\n")
        return track_match['id']
    
    #no-auth
    def search_all_tracks_from_import_playlist(self, import_playlist: list):
        return_list = []
        for song in import_playlist:
            return_list.append(self.search_track(song))
        return return_list

    #no-auth
    def add_playlist_songs_to_export_playlist(self, playlist_id: str):
        for a_song in self.get_all_song_ids_from_playlist(playlist_id):
            song_template = {"title": "", "artists": [], "album": "", "year":"", "duration": 0}
            song = Song(a_song, self.spotify)
            song_template["title"] = song.get_song_title()
            song_template["artists"] = song.get_song_artists_list()
            song_template["album"] = song.get_song_album_name()
            song_template["year"] = song.get_song_year()
            song_template["duration"] = song.get_song_duration_secs()
    
            self.export_playlist.append(song_template)
    
    #no-auth
    def get_export_playlist(self) -> list:
        return self.export_playlist
    
class SpotifyNoAuthBase(SpotifyBase):
    def __init__(self):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                                    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                                    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")))
        self.get_user_results = self._authentication_required
        self.get_playlist_id_from_title = self._authentication_required
        self.set_playlist_thumbnail = self._authentication_required
        self.create_playlist = self._authentication_required 
        self.add_songs_to_playlist = self._authentication_required 
        self.export_playlist = []

    def _authentication_required(self,*args, **kwargs):
        raise ClassicException(msg='UNAUTHENTICATED BRUH, try again', err_code=90)


class Song():
    def __init__(self, songId: str, spotify_obj: Spotify):
        self.song_id = songId
        self.spotify = spotify_obj
        self.song = spotify_obj.track(self.song_id)

    def get_song_id(self) -> str:
        return self.song['id']
    
    def get_song_title(self) -> str:
        return self.song["name"]
    
    def get_song_year(self) -> str:
        year = re.match(r".*(\d{4})(?:\-\d{2}-\d{2}){0,1}", self.song["album"]["release_date"]).group(1)
        return year
    
    def get_song_album_name(self) -> str:
        return self.song['album']['name']
    
    def get_song_album_id(self) -> str:
        return self.song['album']['id']
    
    def get_song_artists_list(self) -> list:
        artist_dict = self.song['artists']
        artist_list = [artist['name'] for artist in artist_dict]
        return artist_list
    
    def get_song_duration_secs(self) -> int:
        return int(self.song["duration_ms"])%1000