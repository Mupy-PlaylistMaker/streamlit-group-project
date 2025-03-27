import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

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

st.set_page_config(page_title="MUPY Search", layout="centered", page_icon="🔍")

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

if "token_info" in st.session_state:
    sp = spotipy.Spotify(auth=st.session_state['token_info']['access_token'])
    user = sp.current_user()

    st.markdown('<div class="logo-text">MUPY Search</div>', unsafe_allow_html=True)
    st.success(f"Logged in as {user['display_name']}")

    st.header("🔍 Explore Spotify by Filters")

    genre = st.text_input("Genre to search for:", value="pop")
    year = st.slider("Released after year:", 2000, 2025, 2015)
    min_popularity = st.slider("Minimum popularity:", 0, 100, 50)
    only_with_preview = st.toggle("Only show tracks with preview", value=False)
    limit = st.slider("Number of tracks to retrieve:", 5, 50, 20)

    query = f'genre:"{genre}" year:{year}-2025'

    if st.button("Search Tracks"):
        try:
            results = sp.search(q=query, type='track', limit=limit)
            filtered = []

            for track in results['tracks']['items']:
                if track['popularity'] < min_popularity:
                    continue
                if only_with_preview and not track['preview_url']:
                    continue
                filtered.append(track)

            st.subheader(f"🎧 Found {len(filtered)} tracks")
            track_uris = []

            for track in filtered:
                st.markdown(f"### {track['name']} by {', '.join(a['name'] for a in track['artists'])}")
                if track['album']['images']:
                    st.image(track['album']['images'][0]['url'], width=150)
                if track['preview_url']:
                    st.audio(track['preview_url'], format="audio/mp3")
                else:
                    st.caption("⚠️ No preview available.")
                st.markdown(f"[▶️ Listen on Spotify]({track['external_urls']['spotify']})")
                st.markdown("---")
                track_uris.append(track['uri'])

            if track_uris:
                st.subheader("📤 Export to Playlist")
                user_playlists = sp.current_user_playlists(limit=50)['items']
                playlist_names = [p['name'] for p in user_playlists]
                playlist_map = {p['name']: p['id'] for p in user_playlists}

                export_option = st.radio("Choose export option:", ["Use Existing Playlist", "Create New Playlist"])

                if export_option == "Use Existing Playlist" and playlist_names:
                    selected_playlist = st.selectbox("Select a playlist:", playlist_names)
                    if st.button("➕ Add All to Playlist"):
                        sp.playlist_add_items(playlist_id=playlist_map[selected_playlist], items=track_uris)
                        st.success(f"✅ Added to '{selected_playlist}'")

                elif export_option == "Create New Playlist":
                    new_name = st.text_input("New playlist name:")
                    if st.button("💼 Create and Add Tracks") and new_name:
                        new_playlist = sp.user_playlist_create(user=user['id'], name=new_name, public=True)
                        sp.playlist_add_items(new_playlist['id'], track_uris)
                        st.success(f"✅ Created playlist '{new_name}'")

        except Exception as e:
            st.error("❌ Search failed.")
            st.exception(e)
else:
    st.markdown('<div class="logo-text">MUPY Search</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>', unsafe_allow_html=True)
