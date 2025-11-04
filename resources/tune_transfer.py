from .yt_base import YTMusicBase
from .spotify_base import SpotifyNoAuthBase, SpotifyBase, ClassicException

class TuneTransfer():
    def __init__(self, from_p: str, to_p: str, playlist_url: str):
        self.playlist_url = playlist_url.strip()
        self.from_p = from_p.lower().replace('music', '').strip()
        self.to_p = to_p.lower().replace('music', '').strip()
        if (self.from_p and self.to_p) not in ['spotify', 'youtube']:
            raise ClassicException("That platform ain't supported buddy!", 30)
        if self.from_p == 'spotify':
            self.from_p = SpotifyNoAuthBase()
        elif self.from_p == 'youtube':
            self.from_p = YTMusicBase()

        if self.to_p == 'spotify':
            self.to_p = SpotifyBase()
        elif self.to_p == 'youtube':
            self.to_p = YTMusicBase()

    def penetrate(self):
        playlist_id = self.from_p.get_playlist_id_from_external_link(self.playlist_url)
        self.from_p.add_playlist_songs_to_export_playlist(playlist_id)
        trans_list = self.from_p.get_export_playlist()


        new_playlist_id = self.to_p.create_playlist(description='BOPS only \U0001F60E')
        all_track_ids = self.to_p.search_all_tracks_from_import_playlist(trans_list)
        if self.to_p.add_songs_to_playlist(new_playlist_id, all_track_ids):
            print('enjoy the new playlist DAWG!')