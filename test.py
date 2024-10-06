import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint
import os
import argparse
from colorama import Fore, Style, init


playlist = 'https://open.spotify.com/playlist/16xhx3JcVMmK82v91klnVh?si=0f51e0b6f275410a'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="db5724867b86424da3ce45cf740632c3",
            client_secret="c1716c31e5674c208a1c6454e84de2ca",
            redirect_uri="http://localhost:8888/callback",
            scope="user-read-playback-state"
        ))

pl = sp.playlist(playlist)

for i in pl['tracks']['items']:
    i = i['track']['external_urls']['spotify']
    print(i)