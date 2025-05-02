# --- Spotify Authentication Setup ---
import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501"
SCOPE = "user-read-private user-read-email"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

# --- Streamlit Page Config ---
st.set_page_config(page_title="MUPY", layout="wide", page_icon="🎷")

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
</style>""", unsafe_allow_html=True)

# --- Spotify Authentication Flow ---
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

# --- Choose Number of Songs to Work With ---
st.sidebar.header("🎚️ Playlist Settings")
num_songs = st.sidebar.slider("How many songs to include?", 10, 50, 20)

# --- Filter Settings ---
st.sidebar.header("🎛️ Filter Songs by Audio Features")

dance_range = st.sidebar.slider("💃 Danceability", 0.0, 1.0, (0.2, 0.8), step=0.2)
valence_range = st.sidebar.slider("😊 Valence (Mood)", 0.0, 1.0, (0.2, 0.8), step=0.2)
tempo_min = int(df["tempo"].min())
tempo_max = int(df["tempo"].max())
tempo_range = st.sidebar.slider("🎵 Tempo (BPM)", tempo_min, tempo_max, (tempo_min, tempo_max), step=5)

# --- Apply filters just once ---
filtered_df = df[
    df["danceability"].between(*dance_range) &
    df["valence"].between(*valence_range) &
    df["tempo"].between(*tempo_range)
]

# --- Initialize or load working_df in session ---
if "working_df" not in st.session_state:
    st.session_state["working_df"] = df.head(0).copy()

# --- Refresh Button ---
if st.sidebar.button("🔄 Refresh Songs"):
    if not filtered_df.empty:
        st.session_state["working_df"] = filtered_df.head(num_songs)
        st.success(f"✅ Found {len(filtered_df)} songs matching your filters.")
    else:
        st.warning("❌ No songs match the selected filters.")
        st.session_state["working_df"] = df.head(0).copy()

# --- Display Results ---
working_df = st.session_state["working_df"]

if not working_df.empty:
    st.subheader(f"🎶 Top {len(working_df)} Filtered Songs")
    st.dataframe(working_df[['artist_name', 'track_name', 'tempo', 'valence', 'danceability']].reset_index(drop=True))
else:
    st.info("🎛️ Adjust the filters and click 'Refresh Songs' to update the list.")



# --- Main Interface ---
if "token_info" in st.session_state:
    if sp_oauth.is_token_expired(st.session_state["token_info"]):
        st.session_state["token_info"] = sp_oauth.refresh_access_token(st.session_state["token_info"]["refresh_token"])
    sp = spotipy.Spotify(auth=st.session_state["token_info"]["access_token"])
    user = sp.current_user()

    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)

   


else:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>', unsafe_allow_html=True)
