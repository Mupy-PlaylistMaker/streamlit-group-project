import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import requests
import numpy as np
import pandas as pd

from ml_model import train_liking_model, predict_like_scores

CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501"
SCOPE = "user-read-private user-read-email user-top-read playlist-modify-public playlist-modify-private"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

st.set_page_config(page_title="MUPY", layout="wide", page_icon="🎷")

features_df = pd.read_csv("Audio_features_cleaned.csv")

# --- CSS Styling ---
st.markdown("""<style>
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
.track-card {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    align-items: center;
    background: #121212;
    padding: 10px;
    border-radius: 10px;
}
.track-card img {
    width: 64px;
    height: 64px;
    object-fit: cover;
    border-radius: 5px;
}
.track-info {
    display: flex;
    flex-direction: column;
}
.track-title {
    font-size: 1.1em;
    font-weight: 600;
    color: #ffffff;
}
.track-meta {
    font-size: 0.9em;
    color: #bbbbbb;
}
</style>""", unsafe_allow_html=True)

# --- Helpers ---
def get_artist_genres(sp, artist_id):
    try:
        return sp.artist(artist_id)['genres']
    except:
        return []

def get_deezer_preview(track_name, artist_name):
    try:
        query = f"{track_name} {artist_name}"
        response = requests.get(f"https://api.deezer.com/search?q={query}")
        data = response.json()
        if data['data']:
            return data['data'][0]['preview']
    except:
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

# --- Main App ---
if "token_info" in st.session_state:
    sp = spotipy.Spotify(auth=st.session_state["token_info"]["access_token"])
    user = sp.current_user()

    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown(f"✅ Logged in as **{user['display_name']}**")

    if user.get("images"):
        st.image(user['images'][0]['url'], width=60)

    mode = st.radio("Choose Mode:", ["🎵 Top Tracks", "🌐 Explore Spotify"])
    popularity_filter = st.selectbox("🎯 Filter by Popularity", [
        "All",
        "🔥 Very Popular (81–100)",
        "👍 Popular (61–80)",
        "🙂 Moderate (41–60)",
        "😐 Low Popularity (0–40)",
    ])
    show_previews_only = st.toggle("Show only tracks with preview", value=False)

    raw_tracks = []
    if mode == "🎵 Top Tracks":
        time_range = st.selectbox("Choose time range", ["short_term", "medium_term", "long_term"],
                                  format_func=lambda x: {
                                      "short_term": "Last 4 Weeks",
                                      "medium_term": "Last 6 Months",
                                      "long_term": "All Time"
                                  }[x])
        limit = st.slider("How many top tracks to show?", 5, 50, 20)
        raw_tracks = sp.current_user_top_tracks(limit=limit, time_range=time_range)["items"]

    elif mode == "🌐 Explore Spotify":
        genre = st.text_input("Genre to search for:", value="pop")
        year = st.slider("Released after year:", 2000, 2025, 2015)
        limit = st.slider("Number of tracks to retrieve:", 5, 50, 20)
        offset = random.randint(0, 1000)
        query = f'genre:"{genre}" year:{year}-2025'

        if st.button("🔀 Shuffle / Search Tracks"):
            try:
                results = sp.search(q=query, type="track", limit=limit, offset=offset)
                raw_tracks = results["tracks"]["items"]
                st.session_state["explore_results"] = raw_tracks
            except Exception as e:
                st.error("❌ Search failed.")
                st.exception(e)

    if mode == "🌐 Explore Spotify" and "explore_results" in st.session_state:
        raw_tracks = st.session_state["explore_results"]

    # Safely get track features
   # Safely get audio features in batches
    track_ids = [track["id"] for track in raw_tracks if track.get("id")]
    unique_track_ids = list(set([tid for tid in track_ids if tid]))

    audio_features = []
    for i in range(0, len(unique_track_ids), 100):
        try:
            ids_batch = unique_track_ids[i:i+100]
            if ids_batch:  # only send non-empty batches
                batch = sp.audio_features(ids_batch)
                if batch:
                    audio_features.extend([f for f in batch if f])
        except Exception as e:
            st.warning(f"Audio feature request failed: {e}")


    feature_keys = ["acousticness", "danceability", "energy", "instrumentalness",
                    "liveness", "loudness", "mode", "speechiness", "tempo",
                    "time_signature", "valence"]

    features_map = {f["id"]: {k: f[k] for k in feature_keys} for f in audio_features if f}

    track_uris = []
    if raw_tracks:
        if "playlist_tracks" not in st.session_state:
            st.session_state["playlist_tracks"] = {}

        st.subheader("🎧 Filtered Tracks")
        for track in raw_tracks:
            track_id = track["id"]
            if not track_id:
                continue

            pop = track["popularity"]
            if popularity_filter == "🔥 Very Popular (81–100)" and pop < 81:
                continue
            elif popularity_filter == "👍 Popular (61–80)" and not (61 <= pop <= 80):
                continue
            elif popularity_filter == "🙂 Moderate (41–60)" and not (41 <= pop <= 60):
                continue
            elif popularity_filter == "😐 Low Popularity (0–40)" and pop > 40:
                continue

            artist_id = track['artists'][0]['id']
            genres = get_artist_genres(sp, artist_id)
            preview_url = track['preview_url'] or get_deezer_preview(track['name'], track['artists'][0]['name'])
            if show_previews_only and not preview_url:
                continue

            if track_id not in st.session_state["playlist_tracks"]:
                st.session_state["playlist_tracks"][track_id] = {"track": track, "liked": True}

            st.session_state["playlist_tracks"][track_id]["track"]["features"] = features_map.get(track_id, {})

            with st.container():
                liked = st.session_state["playlist_tracks"][track_id]["liked"]
                st.markdown(f"""
                <div class="track-card" style="opacity:{'1.0' if liked else '0.5'}">
                    <img src="{track['album']['images'][0]['url'] if track['album']['images'] else ''}" />
                    <div class="track-info">
                        <div class="track-title">{track['name']} — {', '.join(a['name'] for a in track['artists'])}</div>
                        <div class="track-meta">Genres: {', '.join(genres) if genres else 'Unknown'} · Popularity: {pop}</div>
                        <div><a href="{track['external_urls']['spotify']}" target="_blank">▶️ Listen on Spotify</a></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns([1, 5])
                with col1:
                    new_status = not st.checkbox("Change", key=f"chk_{track_id}", value=not liked)
                    st.session_state["playlist_tracks"][track_id]["liked"] = new_status
                with col2:
                    if preview_url:
                        st.audio(preview_url)
                st.markdown("---")

            if st.session_state["playlist_tracks"][track_id]["liked"]:
                track_uris.append(track['uri'])

        # ML Suggestions
        if st.button("Suggest Better Songs with ML"):
            tracks_with_features = [t for t in st.session_state["playlist_tracks"].values() if t["track"].get("features")]
            if tracks_with_features:
                df = pd.DataFrame([t["track"]["features"] for t in tracks_with_features])
                df["liked"] = [int(t["liked"]) for t in tracks_with_features]
                liked_df = df[df["liked"] == 1]
                disliked_df = df[df["liked"] == 0]
                features = [col for col in df.columns if col != "liked"]
                if not disliked_df.empty:
                    model = train_liking_model(liked_df, disliked_df, features)
                    predictions = predict_like_scores(model, df[features])
                    top_indices = np.argsort(predictions)[::-1]

                    st.subheader("🎯 ML Suggested Songs to Keep")
                    for i in top_indices[:5]:
                        t = tracks_with_features[i]["track"]
                        st.markdown(f"**{t['name']}** by {', '.join(a['name'] for a in t['artists'])}")

    if track_uris:
        st.subheader("📤 Export to Playlist")
        user_playlists = sp.current_user_playlists(limit=50)['items']
        playlist_names = [p['name'] for p in user_playlists]
        playlist_map = {p['name']: p['id'] for p in user_playlists}

        export_option = st.radio("Choose an export option:", ["Use Existing Playlist", "Create New Playlist"])

        if export_option == "Use Existing Playlist" and playlist_names:
            selected_playlist = st.selectbox("Select a playlist:", playlist_names)
            if st.button("➕ Add All to Playlist"):
                try:
                    sp.playlist_add_items(playlist_id=playlist_map[selected_playlist], items=track_uris)
                    st.success(f"✅ Added {len(track_uris)} songs to '{selected_playlist}'")
                except Exception as e:
                    st.error("❌ Could not add to playlist.")
                    st.exception(e)

        elif export_option == "Create New Playlist":
            new_name = st.text_input("Name for new playlist:")
            if st.button("💼 Create Playlist and Add Tracks") and new_name.strip():
                try:
                    new_playlist = sp.user_playlist_create(user=user['id'], name=new_name.strip(), public=True)
                    sp.playlist_add_items(new_playlist['id'], track_uris)
                    st.success(f"✅ Created playlist '{new_name}' and added {len(track_uris)} tracks.")
                except Exception as e:
                    st.error("❌ Failed to create or update playlist.")
                    st.exception(e)

else:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>', unsafe_allow_html=True)
