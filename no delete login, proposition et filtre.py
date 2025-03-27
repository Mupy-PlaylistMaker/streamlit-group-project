import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import datetime

# --- Spotify App Credentials ---
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

# --- Streamlit Page Setup ---
st.set_page_config(page_title="MUPY", layout="centered", page_icon="🎧")

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
    </style>
""", unsafe_allow_html=True)

# --- Redirect Handling ---
auth_url = sp_oauth.get_authorize_url()
if "code" in st.query_params:
    code = st.query_params["code"]
    try:
        token_info = sp_oauth.get_access_token(code)
        st.session_state['token_info'] = token_info
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error("Login failed.")
        st.exception(e)

# --- Function to Get Artist Genres ---
def get_artist_genres(sp, artist_id):
    try:
        artist = sp.artist(artist_id)
        return artist['genres']
    except Exception:
        return []

# --- Main Application ---
if "token_info" in st.session_state:
    try:
        sp = spotipy.Spotify(auth=st.session_state['token_info']['access_token'])
        user = sp.current_user()

        if user.get("images"):
            st.markdown(f"<img class='profile-pic' src='{user['images'][0]['url']}' />", unsafe_allow_html=True)

        st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
        st.markdown('<div class="cta-text">Welcome to your Spotify-powered experience!</div>', unsafe_allow_html=True)
        st.markdown("<div class='success-box'>✅ Logged in successfully!</div>", unsafe_allow_html=True)

        st.subheader("👤 Your Profile")
        st.markdown(f"**Name:** {user.get('display_name')}")
        st.markdown(f"**Email:** {user.get('email')}")
        st.markdown(f"**Country:** {user.get('country')}")

        # --- Filters ---
        st.markdown("---")
        st.subheader("🎶 Your Top Tracks")

        time_range = st.selectbox("Choose time range", ["short_term", "medium_term", "long_term"],
                                  format_func=lambda x: {"short_term": "Last 4 Weeks", "medium_term": "Last 6 Months", "long_term": "All Time"}[x])
        track_limit = st.slider("How many top tracks to show?", 5, 50, 20)

        raw_tracks = sp.current_user_top_tracks(limit=track_limit, time_range=time_range)['items']

        # Fetch genres
        all_genres = set()
        enriched_tracks = []

        for track in raw_tracks:
            artist_id = track['artists'][0]['id']
            genres = get_artist_genres(sp, artist_id)
            if genres:
                all_genres.update(genres)
                enriched_tracks.append({"track": track, "genres": genres})

        selected_genres = st.multiselect("🎧 Filter by Artist Genre", sorted(all_genres))

        if selected_genres:
            enriched_tracks = [
                entry for entry in enriched_tracks
                if any(genre in selected_genres for genre in entry['genres'])
            ]

        st.caption(f"🔍 {len(enriched_tracks)} tracks matched your genre filters.")

        if not enriched_tracks:
            st.warning("No tracks match your selected genres.")
        else:
            track_uris = []
            for entry in enriched_tracks:
                track = entry["track"]
                st.markdown(f"### {track['name']} by {', '.join([a['name'] for a in track['artists']])}")
                if track['album']['images']:
                    st.image(track['album']['images'][0]['url'], width=150)
                if track['preview_url']:
                    st.audio(track['preview_url'], format="audio/mp3")
                else:
                    st.caption("⚠️ No preview available.")
                st.markdown(f"**Genres:** {', '.join(entry['genres'])}")
                st.markdown(f"[▶️ Listen on Spotify]({track['external_urls']['spotify']})")
                st.markdown("---")
                track_uris.append(track['uri'])

            # --- Playlist Export ---
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
                if st.button("📀 Create Playlist and Add Tracks") and new_name:
                    try:
                        new_playlist = sp.user_playlist_create(user=user['id'], name=new_name, public=True)
                        sp.playlist_add_items(new_playlist['id'], track_uris)
                        st.success(f"✅ Created playlist '{new_name}' and added {len(track_uris)} tracks.")
                    except Exception as e:
                        st.error("❌ Failed to create or update playlist.")
                        st.exception(e)

    except Exception as e:
        st.error("Something went wrong while fetching your Spotify data.")
        st.exception(e)

else:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>', unsafe_allow_html=True)
