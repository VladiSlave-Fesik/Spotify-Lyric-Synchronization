import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import time
import os
import re


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="db5724867b86424da3ce45cf740632c3",
                                               client_secret="c1716c31e5674c208a1c6454e84de2ca",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-read-playback-state"))


def get_current_track_time():
    current_playback = sp.current_playback()
    if current_playback is not None and current_playback['is_playing']:
        progress_ms = current_playback['progress_ms']
        return progress_ms / 1000
    return None


def read_lrc_file(filepath):
    lyrics = []
    time_tag_pattern = re.compile(r"\[(\d+):(\d+\.\d+)\]")

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            time_tags = time_tag_pattern.findall(line)
            if time_tags:
                for tag in time_tags:
                    minutes, seconds = map(float, tag)
                    time_in_seconds = minutes * 60 + seconds
                    lyrics_text = line.split(']')[-1].strip()
                    if lyrics_text:
                        lyrics.append((time_in_seconds, lyrics_text))
    return lyrics


def display_lyrics(lrc_file):
    lyrics = read_lrc_file(lrc_file)
    current_index = 0

    while current_index < len(lyrics):
        current_time = get_current_track_time()

        if current_time is not None:

            if current_index < len(lyrics) - 1 and current_time >= lyrics[current_index + 1][0]:
                current_index += 1

            print(f"\r{lyrics[current_index][1]}", end='', flush=True)

        time.sleep(0.2)

if __name__ == "__main__":

    lrc_file = os.path.join("lrc", "1. Shepherd of Fire.lrc")
    display_lyrics(lrc_file)

