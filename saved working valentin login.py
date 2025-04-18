import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Spotify OAuth Setup ---
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501"  # Replace with your deployed URL if hosting
SCOPE = "user-read-private user-read-email"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

# --- Streamlit Config ---
st.set_page_config(page_title="MUPY", layout="centered", page_icon="🎧")

# --- CSS Styling Block ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700&display=swap');

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
        transition: background-position 0.5s ease;
        text-align: center;
        margin-top: 60px;
        margin-bottom: 20px;
    }

    .logo-text:hover {
        background-position: right center;
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
        top: 80px;
        left: 80px;
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

# --- Get Auth URL ---
auth_url = sp_oauth.get_authorize_url()
query_params = st.query_params

# --- Handle Redirect with Spotify Code ---
if "code" in st.query_params:
    code = st.query_params["code"]
    try:
        token_info = sp_oauth.get_access_token(code)
        st.session_state['token_info'] = token_info

        # 🔧 Clear query params (the safe way)
        st.query_params.clear()

        # 🔁 Rerun to trigger login view update
        st.rerun()

    except Exception as e:
        st.error("Login failed.")
        st.exception(e)

# --- After Login ---
if "token_info" in st.session_state:
    try:
        sp = spotipy.Spotify(auth=st.session_state['token_info']['access_token'])
        user = sp.current_user()

        # ✅ Profile Picture (top left)
        if user.get("images"):
            st.markdown(
                f"<img class='profile-pic' src='{user['images'][0]['url']}' />",
                unsafe_allow_html=True
            )

        # ✅ Welcome UI
        st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
        st.markdown('<div class="cta-text">Welcome to your Spotify-powered experience!</div>', unsafe_allow_html=True)
        st.markdown("<div class='success-box'>✅ Logged in successfully!</div>", unsafe_allow_html=True)

        # ✅ Show user info
        st.markdown("---")
        st.subheader("Welcome 🎧")
        st.markdown(f"**Name:** {user.get('display_name')}")
        st.markdown(f"**Email:** {user.get('email')}")
        st.markdown(f"**Country:** {user.get('country')}")

    except Exception as e:
        st.error("Something went wrong while retrieving your profile.")
        st.exception(e)
        st.stop()

# --- If Not Logged In ---
else:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>', unsafe_allow_html=True)
