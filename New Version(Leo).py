# Importing needed packages
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify credentials
CLIENT_ID = "61465f148fcb406b856636263e273525"
CLIENT_SECRET = "d96d3207f4da4bc1a7f302685f6f8099"
REDIRECT_URI = " "
SCOPE = "user-read-private user-read-email playlist-modify-private user-library-read user-top-read" # List of interactions with Spotify account authorized for Mupy

# OAuth setup (how the app will have access to the spotify account)
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
)

# Streamlit page configuration
st.set_page_config(page_title="MUPY", layout="centered", page_icon="🎧")


