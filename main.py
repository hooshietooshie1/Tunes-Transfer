import argparse
from resources.tune_transfer import TuneTransfer

def run():
    parser = argparse.ArgumentParser(description="What up homie")
    parser.add_argument("--from_platform", "-fp", type=str, required=True, help="Supported options: Spotify | Youtube")
    parser.add_argument("--to_platform", "-tp", type=str, required=True, help="Supported options: Spotify | Youtube")
    parser.add_argument("--playlist_url", "-pu", type=str, required=True, help="Any public playlist URL on the supported platforms")

    args = parser.parse_args()
    from_platform = args.from_platform
    to_platform = args.to_platform
    playlist_url = args.playlist_url
    tune = TuneTransfer(from_platform, to_platform, playlist_url)
    tune.penetrate()

if __name__ == "__main__":
    run()