import re
from ytmusicapi import YTMusic
from urllib.parse import urlparse, parse_qs
from .common_tools import (generate_random_name, pick_best_match, get_yt_headers_auth)
from .exceptional import ClassicException


##------------------Real action below--------------------


class YTAuth():
    def __init__(self):
        import os
        if not os.path.exists("headers_auth.json"):
            with open("headers_auth.json", 'w') as f:
                pass

        self.ytmusic = YTMusic()

    def is_authenticated(self, ytmusic: YTMusic) -> bool:

        try:
            play = ytmusic.get_library_playlists(limit=5)
            if len(play) == 0:
                return
            return True
        except (Exception) as e:
            if "Unauthorized" in str(e) or "authentication" in str(e).lower():
                return False
            raise ClassicException("UNKNOWN failure", 99)

class YTMusicBase(YTAuth):
    def __init__(self):
        super().__init__()
        if not self.is_authenticated(self.ytmusic):
            try:
                get_yt_headers_auth()
            except:
                raise ClassicException(msg='ERROR AUTHENTICATING YT MUSIC', err_code=90)
        self.ytmusic = YTMusic("headers_auth.json")
        self.channel_id = "YOUR CHANNEL ID"
        self.export_playlist = []

    #auth
    def get_user_results(self):
        return self.ytmusic.get_user(channelId=self.channel_id).get('playlists').get('results')
    
    #auth
    def get_playlist_id_from_title(self, playlist_title: str) -> str:
        for playlist in self.get_user_results():
            if playlist['title'] == playlist_title:
                return playlist['playlistId']
        print(f"No playlist found with name: {playlist_title}")
        raise ClassicException(msg=f"No playlist found with title: {playlist_title}", err_code=10)
    
    #no-auth
    def get_playlist_id_from_external_link(self, url: str):
        try:
            yt_list = parse_qs(urlparse(url).query)
            playlist_id = yt_list.get("list")[0]
            if playlist_id:
                return playlist_id
            else:
                raise ClassicException("INVALID playlist URL, dumbASS!", 30)
        except:
            raise ClassicException("INVALID playlist URL, dumbASS!", 30)
    
    #no-auth
    def get_playlist_thumbnail(self, playlist_id: str):
        return self.ytmusic.get_playlist(playlist_id)['thumbnails'][-1]['url']
    
    #auth
    # def set_playlist_thumbnail() --> DOES NOT EXIST/UNSUPPORTED in ytmusicapi
    
    #no-auth
    def get_all_song_ids_from_playlist(self, playlist_id: str) -> list:
        all_songs_ids = []
        playlist = self.ytmusic.get_playlist(playlist_id)
        for track in playlist.get('tracks'):
            all_songs_ids.append(track.get('videoId'))
        return all_songs_ids
    
    #auth
    def create_playlist(self, random_title: bool = True, description: str = "", user_title: bool = "My Playlist #", thumbnail_url: str = ""):
        return self.ytmusic.create_playlist(user_title if random_title is False else generate_random_name(), description=description, privacy_status='PUBLIC')
    
    #no-auth
    def get_song_id_from_external_link(self, url: str):
        yt_list = parse_qs(urlparse(url).query)
        playlist_id = yt_list.get("v")[0]
        return playlist_id

    #auth
    def add_songs_to_playlist(self, playlist_id: str, video_ids: list):
        if not self.ytmusic.add_playlist_items(playlist_id, video_ids):
            raise ClassicException(msg='ERROR adding songs to playlist', err_code=10)
        else:
            return True

    #no-auth
    def search_track(self, song_dict: dict):
        query_str = f"{song_dict['title']} {", ".join(song_dict['artists'])} {song_dict['album']}"

        results = self.ytmusic.search(query_str, filter='songs', limit=5)
        if not results:
            raise ClassicException(msg="No songs found for: " + f"{song_dict['title']} {", ".join(song_dict['artists'])}", err_code=10)
        
        track_match = pick_best_match('youtube', results, song_dict['title'], song_dict['artists'])
        print(f"Match found! \n" \
              f"Title: {track_match['title']}\n" \
              f"Artists: {[artist['name'] for artist in track_match['artists']]}\n" \
              f"Album: {track_match['album']['name']}\n")
        return track_match['videoId']
    
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
            song = Song(a_song, self.ytmusic)
            song_template["title"] = song.get_song_title()
            song_template["artists"] = song.get_song_artists_list()
            song_template["album"] = song.get_song_album_name()
            song_template["year"] = song.get_song_year()
            song_template["duration"] = song.get_song_duration_secs()

            self.export_playlist.append(song_template)
    
    #no-auth
    def get_export_playlist(self) -> list:
        return self.export_playlist
    
class YTMusicNoAuthBase(YTMusicBase):
    def __init__(self):
        super().__init__()
        self.get_user_results = self._authentication_required
        self.get_playlist_id_from_title = self._authentication_required
        self.create_playlist = self._authentication_required 
        self.add_songs_to_playlist = self._authentication_required 
        self.export_playlist = []

    def _authentication_required(self,*args, **kwargs):
        raise ClassicException(msg='UNAUTHENTICATED BRUH, try again', err_code=90)

class Song():
    def __init__(self, songId: str, ytmusic_obj: YTMusic):
        self.song_id = songId
        self.ytmusic = ytmusic_obj
        self.song = ytmusic_obj.get_song(self.song_id)

    def get_song_id(self) -> str:
        return self.song_id
    
    def get_song_title(self) -> str:
        return self.song["videoDetails"]["title"]
    
    def get_song_year(self) -> str:
        return re.match(r".*(\d{4})-\d{2}-\d{2}.*", self.song["microformat"]["microformatDataRenderer"]["publishDate"]).group(1)
    
    def get_song_album_name(self) -> str:
        search = self.ytmusic.search(f"{self.song["videoDetails"]["title"]} {self.song["videoDetails"]["author"]} {self.get_song_year()}", filter="songs", limit=5)
        for result in search:
            if 'album' in result:
                return result['album']['name']
    
    def get_song_album_id(self) -> str:
        search = self.ytmusic.search(f"{self.song["videoDetails"]["title"]} {self.song["videoDetails"]["author"]} {self.get_song_year()}", filter="songs", limit=5)
        for result in search:
            if 'album' in result:
                return result['album']['id']
    
    def get_song_artists_list(self) -> list:
        return self.song["videoDetails"]["author"] if type(self.song["videoDetails"]["author"]) == list else [self.song["videoDetails"]["author"]]
    
    def get_song_duration_secs(self) -> int:
        return self.song["videoDetails"]["lengthSeconds"]