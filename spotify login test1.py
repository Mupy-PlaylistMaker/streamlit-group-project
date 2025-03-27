import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ======= FILL THESE IN WITH YOUR INFO =======
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "http://localhost:8501/callback"  # Must match what's in your Spotify dev app
SCOPE = "playlist-modify-public playlist-modify-private"

def main():
    st.title("My Spotify App")
    st.write("Welcome! Click below to log in to Spotify.")

    # Initialize Spotipy OAuth
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

    # Generate the Spotify authorization URL
    auth_url = sp_oauth.get_authorize_url()

    # Button that reveals the authorization link
    if st.button("Log In to Spotify"):
        st.write("Click the link to authorize:")
        st.markdown(f"[**Authorize on Spotify**]({auth_url})")

if __name__ == "__main__":
    main()
