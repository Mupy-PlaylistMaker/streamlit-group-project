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
    background: linear-gradient(180deg, #000000, #1a001f, #2a0033, #3f0052);
    color: #eeeeee;
    font-family: 'Outfit', sans-serif;
}
.logo-text {
    font-size: 5em;
    font-weight: 700;
    background: linear-gradient(90deg, #c18dfb, #d8b8ff);
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
    text-decoration: none !important;
    transition: all 0.3s ease-in-out;
    box-shadow: 0 0 20x #1db95466;
}
.login-btn:hover {
    background-color: #1ed760;
    transform: scale(1.05);
    box-shadow: 0 0 28px #1ed760aa;
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
button[kind="secondary"] {
    background-color: #333333 !important;
    color: white !important;
    border: 1px solid #555555 !important;
}
</style>
""", unsafe_allow_html=True)


# --- Helpers ---
def get_album_image_url(sp, track_name, artist_name):
    try:
        results = sp.search(q=f"track:{track_name} artist:{artist_name}", type="track", limit=1)
        time.sleep(0.1)  # Add a small delay to avoid API rate limits
        if results['tracks']['items']:
            return results['tracks']['items'][0]['album']['images'][0]['url']
        return None
    except Exception as e:
        print(f"Error fetching album image for {track_name} by {artist_name}: {e}")
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


def get_valid_tracks(sp, df, num_songs):
    valid_tracks = []
    for _, row in df.iterrows():
        album_image_url = get_album_image_url(sp, row['track_name'], row['artist_name'])
        preview_url = get_deezer_preview(row['track_name'], row['artist_name'])
        if album_image_url and preview_url:
            row['album_image_url'] = album_image_url
            row['preview_url'] = preview_url
            valid_tracks.append(row)
        if len(valid_tracks) >= num_songs:
            break
    return pd.DataFrame(valid_tracks)


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
    return pd.read_csv("1MLNsongs.csv")


df = load_dataset()

# --- Initialize Spotify Client if Logged In ---
if "token_info" in st.session_state:
    # --- Logout Button ---
    with st.sidebar:
        if st.button("🚪 Logout"):
            for key in ["token_info", "working_df", "to_change", "playlist_ready"]:
                if key in st.session_state:
                    del st.session_state[key]
            import os
            if os.path.exists(".cache"):
                os.remove(".cache")
            st.rerun()
    # --- Refresh Button (UI placeholder at top of sidebar) ---
    refresh_clicked = st.sidebar.button("🔄 Refresh Songs")
    sp = spotipy.Spotify(auth=st.session_state["token_info"]["access_token"])

    # --- Initialize session state key for songs marked for replacement ---
    if "to_change" not in st.session_state:
        st.session_state["to_change"] = set()

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
            randomized_df = filtered_df.sample(n=min(num_songs, len(filtered_df)), random_state=random_state)
            return randomized_df
        else:
            return filtered_df


    # --- Choose Number of Songs to Work With ---
    st.sidebar.header("🎚️ Playlist Settings")
    num_songs = st.sidebar.slider("How many songs to include?", 10, 50, 20)

    if "working_df" not in st.session_state:
        st.session_state["working_df"] = pd.DataFrame()
    working_df = st.session_state["working_df"]

    # --- Filter Settings ---
    st.sidebar.header("🎛️ Filter Songs by Audio Features")

    # Genre Dropdown Filter
    genre_options = sorted(df["genre"].dropna().unique().tolist())
    selected_genres = st.sidebar.multiselect("🎼 Select Genres", options=genre_options, default=[])

    df = df[df["genre"].isin(selected_genres)]

    # Popularity filter
    popularity_range = st.sidebar.slider("📈 Popularity", 0, 100, (0, 100))

    # Acousticness filter
    acousticness_range = st.sidebar.slider("🎻 Acousticness", 0.0, 1.0, (0.0, 1.0), step=0.1)

    # Danceability slider
    dance_range = st.sidebar.slider("💃 Danceability", 0.0, 1.0, (0.0, 1.0), step=0.1)

    # Valence (Mood) slider
    valence_range = st.sidebar.slider("😊 Valence (Mood)", 0.0, 1.0, (0.0, 1.0), step=0.1)

    # Tempo slider (BPM)
    if df["tempo"].dropna().empty:
        tempo_min, tempo_max = 0, 250  # fallback default range
    else:
        tempo_min = int(df["tempo"].min())
        tempo_max = int(df["tempo"].max())
    tempo_range = st.sidebar.slider("🎵 Tempo (BPM)", tempo_min, tempo_max, (tempo_min, tempo_max), step=5)

    # Apply filters to df
    df = df[
        df["popularity"].between(*popularity_range) &
        df["acousticness"].between(*acousticness_range)
    ]

    # --- Refresh Button Logic (triggered after all filter variables are defined) ---
    if refresh_clicked:
        oversampled_df = filter_df(df, dance_range, valence_range, tempo_range, num_songs * 3)
        valid_songs_df = get_valid_tracks(sp, oversampled_df, num_songs)
        if not valid_songs_df.empty:
            st.session_state["working_df"] = valid_songs_df
            working_df = valid_songs_df
            st.success(f"✅ Found {len(valid_songs_df)} songs with previews.")
        else:
            st.warning("❌ Couldn't find enough songs with previews.")
            st.session_state["working_df"] = df.head(0).copy()
            working_df = st.session_state["working_df"]

    # --- Apply filters and randomize ---
    filtered_df = filter_df(df, dance_range, valence_range, tempo_range, num_songs)

    # --- Initialize or load working_df in session ---
    if "working_df" not in st.session_state:
        st.session_state["working_df"] = pd.DataFrame()  # Initialize the key with an empty DataFrame


    # --- Step 1: Separate liked and disliked tracks ---
    if 'track_id' in working_df.columns:
        liked_tracks = working_df[~working_df['track_id'].isin(st.session_state["to_change"])]
        disliked_tracks = working_df[working_df['track_id'].isin(st.session_state["to_change"])]
    else:
        liked_tracks = pd.DataFrame()
        disliked_tracks = pd.DataFrame()

    # --- Step 2: Compute mood vector from liked tracks ---
    # Remove "genre" from feature_columns for ML
    feature_columns = [
        'danceability', 'energy', 'valence', 'acousticness', 'instrumentalness',
        'speechiness', 'liveness', 'loudness', 'tempo'
    ]
    # One-hot encode genre if it exists
    if 'genre' in df.columns:
        df = pd.get_dummies(df, columns=["genre"])
    # Redefine feature_columns to include all feature columns used for ML, excluding any non-numeric or ID columns and "genre"
    feature_columns = [col for col in df.columns if col not in ['liked', 'track_id', 'artist_name', 'track_name', 'album_image_url', 'preview_url'] and not col.startswith('genre')]
    # Apply same logic to liked_tracks (ensure columns match after encoding)
    if 'genre' in liked_tracks.columns:
        liked_tracks = pd.get_dummies(liked_tracks, columns=["genre"])
    # Make sure liked_tracks has all columns in feature_columns (fill missing with 0)
    for col in feature_columns:
        if col not in liked_tracks.columns:
            liked_tracks[col] = 0
    if not liked_tracks.empty:
        mood_vector = liked_tracks[feature_columns].mean().values.reshape(1, -1)
    else:
        mood_vector = None  # Fallback if user marks everything for change

    # --- Step 3: Recommend replacements for disliked tracks ---
    # --- Button layout for Replace Disliked Songs ---
    col1, col2 = st.columns([1, 2])
    with col2:
        st.markdown("Click once to load, then click again to replace.", unsafe_allow_html=True)
        replace_clicked = st.button("🔁 Replace Disliked Songs", key="replace_button")
    if replace_clicked and mood_vector is not None and not disliked_tracks.empty:
        # Step 1: Filter the dataset using the same audio feature ranges
        candidate_pool = filter_df(df, dance_range, valence_range, tempo_range, num_songs * 3)
        # Step 2: Remove tracks already liked
        candidate_pool = candidate_pool[~candidate_pool['track_id'].isin(liked_tracks['track_id'])]
        # One-hot encode genre if it exists
        if 'genre' in candidate_pool.columns:
            candidate_pool = pd.get_dummies(candidate_pool, columns=["genre"])
        # Redefine feature_columns to include all feature columns used for ML, excluding any non-numeric or ID columns and "genre"
        feature_columns = [col for col in candidate_pool.columns if col not in ['liked', 'track_id', 'artist_name', 'track_name', 'album_image_url', 'preview_url'] and not col.startswith('genre')]
        # Make sure candidate_pool has all columns in feature_columns (fill missing with 0)
        for col in feature_columns:
            if col not in candidate_pool.columns:
                candidate_pool[col] = 0
        # Step 3: Compute distance to mood vector
        candidate_features = candidate_pool[feature_columns].dropna()
        candidate_vectors = candidate_features.values
        distances = euclidean_distances(candidate_vectors, mood_vector).flatten()
        # Step 4: Add distances back to candidate pool
        candidate_pool = candidate_pool.loc[candidate_features.index].copy()
        candidate_pool['distance'] = distances
        # Step 5: Sort by closest and validate tracks with previews
        sorted_candidates = candidate_pool.sort_values(by='distance')
        replacements_df = get_valid_tracks(sp, sorted_candidates, len(disliked_tracks))
        # Step 6: Replace disliked tracks with new ones
        updated_df = pd.concat([
            liked_tracks,
            replacements_df
        ], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
        st.session_state["working_df"] = updated_df
        st.session_state["to_change"] = set()
        st.success("🔁 Disliked tracks replaced with similar suggestions.")


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

            change_selected = st.checkbox("✅ Mark for change", key=f"change_{track['track_id']}")
            if change_selected:
                st.session_state["to_change"].add(track['track_id'])
            else:
                st.session_state["to_change"].discard(track['track_id'])

            # Display the preview
            if preview_url:
                st.audio(preview_url, format="audio/mp3")

        # --- Enhanced Pentagon Radar Chart for Playlist Profile ---
        import matplotlib.pyplot as plt
        import numpy as np

        radar_features = ['danceability', 'popularity', 'valence', 'acousticness', 'instrumentalness']

        if all(f in working_df.columns for f in radar_features) and not working_df.empty:
            avg_values = working_df[radar_features].mean()
            if avg_values['popularity'] > 1:
                avg_values['popularity'] /= 100

            values = avg_values.tolist()
            values += values[:1]

            angles = np.linspace(0, 2 * np.pi, len(radar_features), endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))

            # Improve color and theme consistency
            ax.fill(angles, values, color='#b388eb', alpha=0.3)
            ax.plot(angles, values, color='#ff4ecb', linewidth=2)

            # Enhanced labels and theme matching
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(radar_features, fontsize=12, color='white', fontweight='bold')
            ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], color='#cccccc', fontsize=8)
            ax.set_ylim(0, 1)

            ax.tick_params(colors='white')
            ax.spines['polar'].set_color('white')
            ax.grid(color='#444444', linestyle='dotted', linewidth=0.8)
            fig.patch.set_facecolor('#0b0011')
            ax.set_facecolor('#0b0011')

            # Title styling
            ax.set_title("🎯 Playlist Audio Profile", y=1.1, color='#eeeeee', fontsize=14, fontweight='bold')

            st.pyplot(fig)

        # --- Export to Spotify Playlist ---
        st.markdown("---")
        st.subheader("📤 Export to Spotify")

        playlist_name = st.text_input("Enter a name for your new playlist:", value="My MUPY Playlist")

        if st.button("🎧 Create Spotify Playlist"):
            try:
                user_id = sp.current_user()["id"]
                new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
                track_ids = working_df['track_id'].dropna().tolist()
                track_uris = [f"spotify:track:{tid}" for tid in track_ids]
                if track_uris:
                    sp.playlist_add_items(new_playlist["id"], track_uris)
                    st.success(f"✅ Playlist '{playlist_name}' created and tracks added!")
                else:
                    st.warning("No valid Spotify track IDs found to add.")
            except Exception as e:
                st.error("Failed to create playlist or add tracks.")
                st.exception(e)
    else:
        st.info("🎛️ Adjust the filters and click 'Refresh Songs' to update the list.")

else:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>',
                unsafe_allow_html=True)
