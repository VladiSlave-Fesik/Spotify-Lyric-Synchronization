import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
import re
from colorama import init, Fore, Back, Style, ansi

# Initialize colorama
init()

def rgb_to_ansi_256(r, g, b):
    """
    Convert RGB color to the closest ANSI 256-color code.

    :param r: Red value (0-255)
    :param g: Green value (0-255)
    :param b: Blue value (0-255)
    :return: ANSI escape code for the closest 256-color
    """
    if r == g == b:
        if r < 8:
            return f'\033[38;5;16m'
        if r > 248:
            return f'\033[38;5;231m'
        return f'\033[38;5;{round(((r - 8) / 247) * 24) + 232}m'

    ansi = 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)
    return f'\033[38;5;{ansi}m'

# Color customization
background_color = Back.BLACK
text_color = Fore.WHITE
highlight_color = rgb_to_ansi_256(240, 120, 0)  # Orange
progress_bar_color = rgb_to_ansi_256(240, 120, 0)  # Orange
progress_bar_back_color = rgb_to_ansi_256(50, 50, 50)  # Dark gray
play_icon_color = rgb_to_ansi_256(0, 240, 204)  # Cyan
pause_icon_color = rgb_to_ansi_256(240, 76, 0)  # Orange/
artist_color = rgb_to_ansi_256(240, 120, 0)  # Orange
time_color = rgb_to_ansi_256(150, 150, 150)  # Medium gray
current_lyric_color = highlight_color
other_lyric_color = text_color

# Symbol customization
play_symbol = '▶'
pause_symbol = '❚❚'
progress_bar_fill = '█'
progress_bar_empty = '▒'

padding = ' ' * 1


# Clear screen function
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="db5724867b86424da3ce45cf740632c3",
                                               client_secret="c1716c31e5674c208a1c6454e84de2ca",
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-read-playback-state,user-modify-playback-state"))

def get_current_playback_info():
    """Get information about the current track."""
    current_playback = sp.current_playback()
    if current_playback is not None:
        is_playing = current_playback['is_playing']
        progress_ms = current_playback['progress_ms']
        duration_ms = current_playback['item']['duration_ms']
        track_name = current_playback['item']['name']
        artist_name = ', '.join([artist['name'] for artist in current_playback['item']['artists']])
        return is_playing, progress_ms / 1000, duration_ms / 1000, track_name, artist_name
    return None, None, None, None, None

def read_lrc_file(filepath):
    """Read .lrc file and parse lines."""
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
    return sorted(lyrics, key=lambda x: x[0])

def format_time(seconds):
    """Format time in seconds to MM:SS format."""
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

def move_cursor(x, y):
    """Move cursor to a specific position."""
    print(ansi.Cursor.POS(x, y), end='')

def clear_line():
    """Clear the current line."""
    print(ansi.clear_line(), end='')


def find_current_lyric(lyrics, current_time):
    """Find the current lyric based on the current time."""
    for i, (time, text) in enumerate(lyrics):
        if time > current_time:
            if i > 0:
                return i - 1, lyrics[i - 1][1]
            else:
                return 0, ""
    return len(lyrics) - 1, lyrics[-1][1]

def custom_progress_bar(current, total, width=50):
    """Create a custom progress bar."""
    filled_length = int(width * current // total)
    bar = progress_bar_color + progress_bar_fill * filled_length + progress_bar_back_color + progress_bar_empty * (width - filled_length)
    return bar + Style.RESET_ALL

def display_lyrics(lrc_file, track_name, artist_name):
    """Display synchronized lyrics."""
    lyrics = read_lrc_file(lrc_file)
    prev_track = track_name
    prev_lyric_index = -1

    try:
        while True:
            is_playing, current_time, duration, current_track_name, current_artist_name = get_current_playback_info()

            if current_track_name != prev_track:
                lrc_file = os.path.join("lrc", f"{current_artist_name} - {current_track_name}.lrc")
                if os.path.exists(lrc_file):
                    lyrics = read_lrc_file(lrc_file)
                else:
                    lyrics = []
                prev_track = current_track_name
                prev_lyric_index = -1

            # Move cursor to top and start updating
            move_cursor(1, 1)

            # Display track info
            clear_line()
            print(f"{background_color}{text_color}Now Playing: {highlight_color}{current_track_name}{text_color} by {artist_color}{current_artist_name}{Style.RESET_ALL}")

            # Display play/pause status and progress bar
            move_cursor(1, 2)
            clear_line()
            progress_bar = custom_progress_bar(current_time, duration)
            status = f"{play_icon_color}{play_symbol}{Style.RESET_ALL}" if is_playing else f"{pause_icon_color}{pause_symbol}{Style.RESET_ALL}"
            print(f"{background_color}{status} {progress_bar} {time_color}{format_time(current_time)} | {format_time(duration)}{Style.RESET_ALL}")

            # Find and display current lyrics
            if lyrics:
                current_index, current_lyric = find_current_lyric(lyrics, current_time)

                if current_index != prev_lyric_index:
                    for i in range(5):
                        move_cursor(1, 4 + i)
                        clear_line()
                        if 0 <= current_index - 2 + i < len(lyrics):
                            _, lyric_text = lyrics[current_index - 2 + i]
                            if i == 2:  # Current lyric
                                print(f"{background_color}{padding}{current_lyric_color}{lyric_text}{Style.RESET_ALL}")
                            else:
                                print(f"{background_color}{padding}{other_lyric_color}{lyric_text}{Style.RESET_ALL}")
                        else:
                            print(f"{background_color} {Style.RESET_ALL}")  # Print an empty line if no lyrics
                    prev_lyric_index = current_index
            else:
                for i in range(5):
                    move_cursor(1, 4 + i)
                    clear_line()
                    if i == 2:
                        print(f"{background_color}{highlight_color}[Lyrics not found]{Style.RESET_ALL}")
                    else:
                        print(f"{background_color} {Style.RESET_ALL}")  # Print empty lines

            time.sleep(0.1)
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    clear_screen()  # Clear screen before starting the main loop
    try:
        while True:
            is_playing, current_time, duration, track_name, artist_name = get_current_playback_info()
            if track_name and artist_name:
                lrc_file = os.path.join("lrc", f"{artist_name} - {track_name}.lrc")
                if os.path.exists(lrc_file):
                    display_lyrics(lrc_file, track_name, artist_name)
                else:
                    print(f"{background_color}{highlight_color}[Lyrics not found for: {track_name}]{Style.RESET_ALL}")
                    time.sleep(2)
            else:
                print(f"{background_color}{highlight_color}[No track is currently playing]{Style.RESET_ALL}")
                time.sleep(2)
    except KeyboardInterrupt:
        clear_screen()
        print(f"{background_color}{highlight_color}The program has been completed by the user. Thank you for using it!{Style.RESET_ALL}")
    except Exception as e:
        print(f"{background_color}{highlight_color}There was an error: {e}{Style.RESET_ALL}")
    finally:
        print(f"{background_color}{highlight_color}Exiting the program...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()