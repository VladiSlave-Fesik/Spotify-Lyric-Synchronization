import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import argparse
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama for colored output on all platforms
init(autoreset=True)


# Function to get track info from a Spotify URL
def get_track_info(spotify_url):
    try:
        # Setup Spotify API with client_id, client_secret, and redirect_uri
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="db5724867b86424da3ce45cf740632c3",
            client_secret="c1716c31e5674c208a1c6454e84de2ca",
            redirect_uri="http://localhost:8888/callback",
            scope="user-read-playback-state"
        ))

        # Extract track ID from the Spotify URL
        track_id = spotify_url.split('/')[-1].split('?')[0]
        # Fetch track info
        track = sp.track(track_id)

        track_name = track['name']
        artists = ', '.join([artist['name'] for artist in track['artists']])

        return track_name, artists

    except Exception as e:
        tqdm.write(Fore.RED + f"[!] Error fetching track info: {str(e)}")
        return None, None


# Function to search and download .lrc file via the lrclib.net API
def download_lrc(track_name, artist_name, save_dir="lrc"):
    url = f"https://lrclib.net/api/get?artist_name={'+'.join(artist_name.split())}&track_name={'+'.join(track_name.split())}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data and data.get('syncedLyrics'):
                lrc_content = data['syncedLyrics']

                # Create directory if it does not exist
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                # Save the .lrc file to the specified directory
                lrc_filename = os.path.join(save_dir, f"{artist_name} - {track_name}.lrc")
                with open(lrc_filename, 'w', encoding='utf-8') as lrc_file:
                    lrc_file.write(lrc_content)

                return True  # Successfully downloaded
            else:
                return False  # No .lrc found
        else:
            return False  # Error in response
    except requests.exceptions.RequestException as e:
        return False  # Request failed


# Function to handle track or playlist URLs
def handle_spotify_url(spotify_url, save_dir):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="db5724867b86424da3ce45cf740632c3",
        client_secret="c1716c31e5674c208a1c6454e84de2ca",
        redirect_uri="http://localhost:8888/callback",
        scope="user-read-playback-state"
    ))

    track_urls = []

    # Check if it's a track or playlist
    if "track" in spotify_url:
        track_urls.append(spotify_url)
    elif "playlist" in spotify_url:
        pl = sp.playlist(spotify_url)
        for item in pl['tracks']['items']:
            track_urls.append(item['track']['external_urls']['spotify'])

    downloaded_tracks = 0
    failed_tracks = []

    # Progress bar with tqdm
    for track_url in tqdm(track_urls, desc="Downloading .lrc files", ncols=100, unit="track", leave=False, colour='cyan'):
        track_name, artist_name = get_track_info(track_url)
        if track_name and artist_name:
            if download_lrc(track_name, artist_name, save_dir):
                downloaded_tracks += 1
            else:
                failed_tracks.append(f"{track_name} - {artist_name}")
        else:
            failed_tracks.append(f"Invalid track info for {track_url}")

    # Summary after downloading
    tqdm.write(Fore.GREEN + f"\n[✔] Downloaded {downloaded_tracks} tracks.")
    if failed_tracks:
        tqdm.write(Fore.RED + f"[!] Failed to download {len(failed_tracks)} tracks:")
        for failed_track in failed_tracks:
            tqdm.write(Fore.RED + f" - {failed_track}")


def main():
    while True:
        parser = argparse.ArgumentParser(description="Download .lrc files for Spotify tracks or playlists.")
        parser.add_argument("--url", type=str, help="Spotify track or playlist URL.")
        parser.add_argument("--save-dir", type=str, default="lrc",
                            help="Directory to save the .lrc file (default: 'lrc').")

        args = parser.parse_args()

        spotify_url = args.url if args.url else input(Fore.CYAN + "Enter Spotify track or playlist URL: ")
        if not spotify_url:
            print(Fore.RED + "[!] No URL provided. Exiting.")
            break

        save_dir = args.save_dir if args.save_dir else input(
            Fore.CYAN + "Enter directory to save .lrc file (default 'lrc/'): ") or "lrc"

        # Handle track or playlist URL
        handle_spotify_url(spotify_url, save_dir)

        print(Fore.CYAN + "\n[i] Press Enter to exit or input another URL.")
        next_input = input(Fore.CYAN + "Enter Spotify track or playlist URL: ")
        if not next_input:
            print(Fore.CYAN + "[i] Exiting program.")
            break


if __name__ == "__main__":
    main()
