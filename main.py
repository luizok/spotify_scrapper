import os

from dotenv import load_dotenv

from spotify_scrapper import SpotifyScrapper


if __name__ == '__main__':

    load_dotenv(override=True)

    scrapper = SpotifyScrapper(
        username=os.getenv('SPOTIFY_USERNAME'),
        password=os.getenv('SPOTIFY_PASSWORD')
    )

    playlists = scrapper.get_playlists()
    tracks = scrapper.get_playlist('collection')

    print(f'Got {len(tracks)} tracks')
