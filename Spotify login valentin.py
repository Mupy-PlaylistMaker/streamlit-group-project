import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Spotify Credentials ---
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "https://spotify20appleopy-wr6jzbaagwn9sxdzmtmjwl.streamlit.app/"
SCOPE = "user-read-private user-read-email"

# --- OAuth Setup ---
sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

# --- Streamlit Config ---
st.set_page_config(page_title="MUPY", layout="centered", page_icon="🎧")

# --- CSS Styling ---
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

    @keyframes fadein {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
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
        animation: fadein 1s ease-in-out;
    }

    .profile-pic {
        position: fixed;
        top: 20px;
        left: 20px;
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

# --- Get auth URL
auth_url = sp_oauth.get_authorize_url()

# --- Read query params safely
query_params = st.query_params()

# --- Handle Spotify redirect
if "code" in query_params:
    try:
        code = query_params["code"][0]  # it's a list!
        token_info = sp_oauth.get_access_token(code)
        if token_info:
            st.session_state['token_info'] = token_info
            st.rerun()
        else:
            st.error("Spotify token retrieval failed.")
    except Exception as e:
        st.error(f"Login failed: {e}")

# --- UI before login
if "token_info" not in st.session_state:
    st.markdown('<div class="logo-text">MUPY</div>', unsafe_allow_html=True)
    st.markdown('<div class="cta-text">Login with Spotify to start your journey</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Log in with Spotify</a></div>', unsafe_allow_html=True)

# --- After login
if "token_info" in st.session_state:
    try:
        sp = spotipy.Spotify(auth=st.session_state['token_info']['access_token'])
        user = sp.current_user()

        # ✅ Show success message
        st.markdown("<div class='success-box'>✅ Logged in successfully!</div>", unsafe_allow_html=True)

        # ✅ Profile picture top-left
        if user.get('images') and user['images']:
            st.markdown(
                f"<img class='profile-pic' src='{user['images'][0]['url']}' />",
                unsafe_allow_html=True
            )

        # ✅ User info section
        st.subheader("Welcome 🎧")
        st.markdown(f"**Name:** {user.get('display_name', 'Unknown')}")
        st.markdown(f"**Email:** {user.get('email', 'Not available')}")
        st.markdown(f"**Country:** {user.get('country', 'Not available')}")

    except Exception as e:
        st.error("Something went wrong while loading your Spotify profile.")
        st.exception(e)
