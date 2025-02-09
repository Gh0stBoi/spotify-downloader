from flask import Flask, request, jsonify, render_template
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import re

app = Flask(__name__)

# 🔑 Spotify API credentials
SPOTIFY_CLIENT_ID = "f779e3648db244f1a9dcacb59e1568a0"
SPOTIFY_CLIENT_SECRET = "f9926e8911ce44b8b17deff3d94722b1"

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

def get_playlist_tracks(playlist_url):
    playlist_id = re.search(r"playlist/(\w+)", playlist_url).group(1)
    results = sp.playlist_tracks(playlist_id)
    
    tracks = [f"{item['track']['name']} {item['track']['artists'][0]['name']}" for item in results['items']]
    return tracks

def download_song(song_name):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f"static/downloads/{song_name}.%(ext)s",
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"ytsearch:{song_name} audio"])

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/download', methods=['POST'])
def download():
    playlist_url = request.form.get("playlist_url")
    if not playlist_url:
        return jsonify({"error": "No playlist URL provided"}), 400

    tracks = get_playlist_tracks(playlist_url)

    for song in tracks:
        download_song(song)

    return jsonify({"message": "Download complete!", "songs": tracks})

if __name__ == "__main__":
    app.run(debug=True)
