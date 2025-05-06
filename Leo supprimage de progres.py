import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import requests
import pandas as pd
import numpy as np
import time
from sklearn.metrics.pairwise import euclidean_distances

# --- Configuration ---
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501"
SCOPE = "user-read-private user-read-email playlist-modify-public playlist-modify-private"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

st.set_page_config(page_title="MUPY", layout="wide", page_icon="🎷")

# --- CSS Styling ---
st.markdown("""
<style>
html, body, .stApp {
    background: linear-gradient(to bottom, #000000, #0b0011);
    color: #eeeeee;
    font-family: 'Outfit', sans-serif;
}
.logo-text {
    font-size: 4em;
    font-weight: 700;
    background: linear-gradient(90deg, #ff4ecb, #b388eb);
    background-size: 200% auto;
    color: transparent;
    background-clip: text;
    -webkit-background-clip: text;
    text-align: center;
    margin-top: 60px;
    margin-bottom: 20px;
}
.cta-text {
    font-size: 1.5em;
    text-align: center;
    margin-bottom: 50px;
    color: #cccccc;
}
.login-btn {
    display: inline-block;
    background-color: #1db954;
    color: white !important;
    padding: 0.9em 2.2em;
    border-radius: 30px;
    font-weight: 600;
    font-size: 1.1em;
    text-decoration: none;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 0 10px #1db95466;
}
.login-btn:hover {
    background-color: #1ed760;
    transform: scale(1.05);
    box-shadow: 0 0 14px #1ed760aa;
}
.center-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.success-box {
    background-color: #1a1f1b;
    border-left: 5px solid #1db954;
    padding: 1em;
    margin-top: 60px;
    margin-bottom: 60px;
    border-radius: 10px;
    font-weight: 500;
    color: #d4fcdc;
    text-align: center;
    width: 80%;
    margin-left: auto;
    margin-right: auto;
}
.profile-pic {
    position: fixed;
    top: 20px;
    left: 50px;
    border-radius: 50%;
    width: 60px;
    height: 60px;
    border: 2px solid #b388eb;
    object-fit: cover;
    z-index: 999;
    box-shadow: 0 0 10px #b388eb88;
}
.track-card {
    display: flex;
    background-color: #1a1f1b;
    border-radius: 15px;
    margin: 10px;
    padding: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease-in-out;
}
.track-card:hover {
    transform: scale(1.05);
}
.track-card img {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    margin-right: 10px;
}
.track-info {
    flex-grow: 1;
}
.track-title {
    font-size: 1.2em;
    color: #fff;
}
.track-meta {
    font-size: 0.9em;
    color: #aaa;
}
</style>
""", unsafe_allow_html=True)


# --- Helpers ---
def get_album_image_url(sp, track_name, artist_name):
    try:
        results = sp.search(q=f"track:{track_name} artist:{artist_name}", type="track", limit=1)
        if results['tracks']['items']:
            track = results['tracks']['items'][0]
            album_image_url = track['album']['images'][0]['url']
            return album_image_url
        else:
            return None
    except Exception as e:
        st.error("Error fetching album image.")
        return None


def get_deezer_preview(track_name, artist_name):
    try:
        query = f"{track_name} {artist_name}"
        response = requests.get(f"https://api.deezer.com/search?q={query}")
        data = response.json()
        if data['data']:
            return data['data'][0]['preview']
        return None
    except Exception as e:
        st.error("Error fetching Deezer preview.")
        return None


# --- Auth ---
auth_url = sp_oauth.get_authorize_url()
if "code" in st.query_params:
    code = st.query_params["code"]
    try:
        token_info = sp_oauth.get_access_token(code)
        st.session_state["token_info"] = token_info
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error("Login failed.")
        st.exception(e)


# --- Load Dataset ---
@st.cache_data
def load_dataset():
    return pd.read_csv("cleaned_spotify_dataset.csv")


df = load_dataset()

# --- Initialize Spotify Client if Logged In ---
if "token_info" in st.session_state:
    sp = spotipy.Spotify(auth=st.session_state["token_info"]["access_token"])

    # --- Filter Helper Function ---
    def filter_df(df, dance_range, valence_range, tempo_range, num_songs):
        # Apply filters
        filtered_df = df[
            df["danceability"].between(*dance_range) &
            df["valence"].between(*valence_range) &
            df["tempo"].between(*tempo_range)
            ]

        # Randomize the order of the songs
        if not filtered_df.empty:
            random_state = int(time.time())  # Use time-based random state for more variability
            randomized_df = filtered_df.sample(n=num_songs, random_state=random_state)
            return randomized_df
        else:
            return filtered_df

    # --- Choose Number of Songs to Work With ---
    st.sidebar.header("🎚️ Playlist Settings")
    num_songs = st.sidebar.slider("How many songs to include?", 10, 50, 20)

    # --- Filter Settings ---
    st.sidebar.header("🎛️ Filter Songs by Audio Features")

    # Divide danceability into 3 categories
    danceability_category = st.sidebar.radio(
        "💃 Danceability",
        ['Low', 'Medium', 'High']
    )

    if danceability_category == 'Low':
        dance_range = (0.0, 0.3)
    elif danceability_category == 'Medium':
        dance_range = (0.3, 0.7)
    elif danceability_category == 'High':
        dance_range = (0.7, 1.0)

    # Divide valence (mood) into 3 categories
    valence_category = st.sidebar.radio(
        "😊 Valence (Mood)",
        ['Low', 'Medium', 'High']
    )

    if valence_category == 'Low':
        valence_range = (0.0, 0.3)
    elif valence_category == 'Medium':
        valence_range = (0.3, 0.7)
    elif valence_category == 'High':
        valence_range = (0.7, 1.0)

    # Tempo Category Selection (Slow, Mid, Fast)
    bpm_category = st.sidebar.radio("🎵 Select Tempo Category", ["Slow", "Mid", "Fast"])
    if bpm_category == "Slow":
        tempo_range = (0, 90)
    elif bpm_category == "Mid":
        tempo_range = (90, 130)
    elif bpm_category == "Fast":
        tempo_range = (130, 249)

    # --- Apply filters and randomize ---
    filtered_df = filter_df(df, dance_range, valence_range, tempo_range, num_songs)

    # --- Initialize or load working_df in session ---
    if "working_df" not in st.session_state:
        st.session_state["working_df"] = pd.DataFrame()  # Initialize the key with an empty DataFrame

    # --- Refresh Button ---
    if st.sidebar.button("🔄 Refresh Songs"):
        randomized_songs = filter_df(df, dance_range, valence_range, tempo_range, num_songs)
        if not randomized_songs.empty:
            st.session_state["working_df"] = randomized_songs
            st.success(f"✅ Found and randomized {len(randomized_songs)} songs matching your filters.")
        else:
            st.warning("❌ No songs match the selected filters.")
            st.session_state["working_df"] = df.head(0).copy()

    working_df = st.session_state["working_df"]

    if not working_df.empty:
        st.subheader(f"🎶 Top {len(working_df)} Filtered Songs")

        # List to store valid tracks that are found
        valid_tracks = []

        for index, row in working_df.iterrows():
            # Fetch album image for the track
            album_image_url = get_album_image_url(sp, row['track_name'], row['artist_name'])
            # Fetch preview URL from Deezer
            preview_url = get_deezer_preview(row['track_name'], row['artist_name'])

            if album_image_url and preview_url:  # Only include tracks that have both album images and preview URL
                valid_tracks.append(row)

        # Display the valid tracks with album images and previews
        for track in valid_tracks:
            album_image_url = get_album_image_url(sp, track['track_name'], track['artist_name'])
            preview_url = get_deezer_preview(track['track_name'], track['artist_name'])
            st.markdown(f"""
                   <div class="track-card">
                       <img src="{album_image_url}" />
                       <div class="track-info">
                           <div class="track-title">{track['track_name']} — {track['artist_name']}</div>
                       </div>
                   </div>
                   """, unsafe_allow_html=True)

            # Display the preview
            if preview_url:
                st.audio(preview_url, format="audio/mp3")
    else:
        st.info("🎛️ Adjust the filters and click 'Refresh Songs' to update the list.")

else:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>',
                unsafe_allow_html=True)

