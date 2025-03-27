import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify credentials
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501"
SCOPE = "user-read-private user-read-email"

sp_oauth = SpotifyOAuth(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        redirect_uri=REDIRECT_URI,
                        scope=SCOPE)

auth_url = sp_oauth.get_authorize_url()
query_params = st.query_params

# --- Page config ---
st.set_page_config(page_title="Mupy", layout="centered", page_icon="🟣")

# --- Custom minimalist styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600&display=swap');

    html, body, .stApp {
    background-color: #000000 !important;
    color: #eeeeee;
    font-family: 'Outfit', sans-serif;
}


    .title {
        font-size: 3.5em;
        font-weight: 600;
        color: #b388eb;
        margin-top: 30px;
    }

    .login-btn {
        background-color: #b388eb;
        color: black !important;
        padding: 0.75em 2.2em;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.1em;
        text-decoration: none;
        transition: all 0.25s ease-in-out;
        border: none;
    }

    .login-btn:hover {
        background-color: #d1aaff;
        color: black !important;
        text-decoration: none;
    }

    .section {
        text-align: center;
        margin-top: 50px;
    }

    .brand-icon {
        width: 80px;
        margin-bottom: 10px;
        opacity: 0.95;
    }

    .divider {
        margin-top: 40px;
        border-top: 1px solid #333333;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- UI Layout ---
st.markdown('<div class="section">', unsafe_allow_html=True)
st.image("https://cdn-icons-png.flaticon.com/512/5968/5968852.png", width=80)  # Clean music icon
st.markdown('<div class="title">Mupy</div>', unsafe_allow_html=True)
st.markdown(f'<a class="login-btn" href="{auth_url}">Log in with Spotify</a>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Spotify redirect ---
if "code" in query_params:
    code = query_params["code"]
    token_info = sp_oauth.get_access_token(code)
    st.session_state['token_info'] = token_info
    st.success("Logged in successfully.")
    st.experimental_rerun()

# --- User section after login ---
if 'token_info' in st.session_state:
    sp = spotipy.Spotify(auth=st.session_state['token_info']['access_token'])
    user = sp.current_user()

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.subheader("Your Spotify Profile")

    if user['images']:
        st.image(user['images'][0]['url'], width=100)

    st.markdown(f"**Name:** {user['display_name']}")
    st.markdown(f"**Email:** {user['email']}")
    st.markdown(f"**Country:** {user['country']}")
