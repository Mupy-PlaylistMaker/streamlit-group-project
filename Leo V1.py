import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Spotify Credentials ---
CLIENT_ID = "61465f148fcb406b856636263e273525"
CLIENT_SECRET = "d96d3207f4da4bc1a7f302685f6f8099"
REDIRECT_URI = "mupyplaylistmaker.streamlit.app/callback"
SCOPE = "user-read-private user-read-email"

# --- OAuth Setup ---
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

# --- Streamlit Config ---
st.set_page_config(page_title="Mupy", layout="centered", page_icon="🎧")

# --- CSS Styling ---
st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #000000; /* Full black background */
    }
    .logo-text {
        font-size: 4em;
        font-weight: 700;
        color: #ADD8E6; /* Pastel blue */
        text-align: center;
        margin-top: 20vh; /* Push title down */
        transition: color 0.3s ease;
    }
    .logo-text:hover {
        color: #8A2BE2; /* Violet on hover */
    }
    .login-btn {
        display: block;
        background-color: #8A2BE2; /* Violet */
        color: white !important;
        font-size: 1.2em;
        padding: 1em 2em;
        text-align: center;
        border-radius: 8px;
        width: 200px;
        margin: 2em auto;
        text-decoration: none;
    }
    .center-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- Get Spotify Auth URL ---
auth_url = sp_oauth.get_authorize_url()

# --- Read Query Parameters ---
query_params = st.query_params

# --- Handle Spotify Redirect and Token Exchange ---
if "code" in query_params:
    try:
        code = query_params["code"][0]
        token_info = sp_oauth.get_access_token(code)
        if token_info:
            st.session_state["token_info"] = token_info
            st.experimental_rerun()
        else:
            st.error("Spotify token retrieval failed.")
    except Exception as e:
        st.error("Login failed.")
        st.exception(e)

# --- UI BEFORE Login ---
if "token_info" not in st.session_state:
    st.markdown('<div class="logo-text">Mupy</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="center-box"><a class="login-btn" href="{auth_url}">Login with Spotify</a></div>', unsafe_allow_html=True)

# --- UI AFTER Login ---
if "token_info" in st.session_state:
    # Placeholder logged-in page (full black background)
    st.markdown("""
        <div style="text-align: center; margin-top: 30vh; color: white; font-size: 2em;">
            Logged in successfully! (Placeholder page)
        </div>
    """, unsafe_allow_html=True)
