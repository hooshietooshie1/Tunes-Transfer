
# Tunes Transfer

Transfer public playlists between distinct music platforms, currently including Spotify & Youtube Music.






## Platform libraries used

[Spotify](https://spotipy.readthedocs.io/en/2.25.1/)- OAuth2 authentication

[YTMusicAPI](https://ytmusicapi.readthedocs.io/en/latest/index.html) - Cookie-based authentication


## Persistent Data

The app will create/re-use the following files in/from cwd.

`headers_auth.json` (YT Music)

`ytmusic_cookies.json` (YT Music)

`.cache` (Spotify)



## Usage (standalone .exe) 

Just double-click the "TunesTransfer.exe" file, nothing else needed!

## Usage (with Python 3.13+ installed) 

```sh
pip install -r ./requirements.txt
```
```sh
python_path main.py -fp <youtube/spotify> -tp <spotify/youtube> -pu "<playlist URL>"
```

```sh
## For help

python_path main.py -h
```

made w/ ❤️