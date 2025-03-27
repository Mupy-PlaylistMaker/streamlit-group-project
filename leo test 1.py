import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ---- Replace these with your actual Spotify app credentials ----
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501/callback"  # or your actual callback URL
SCOPE = "user-library-read playlist-modify-private"

def main():
    # --- Custom CSS for a violet-lilac palette ---
    st.markdown("""
        <style>
        body {
            background-color: #E6E6FA; /* light lavender */
        }
        h1 {
            color: #8A2BE2;           /* blue-violet for the main title */
            text-align: center;
            font-size: 3rem;
        }
        .stButton button {
            background-color: #9370DB; /* medium purple */
            color: #FFFFFF;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 1.25rem;
            font-size: 1rem;
            cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Page Title ---
    st.title("Mupy")

    st.write("Welcome to the Mupy home page. Click below to log in with Spotify.")

    # --- Set up Spotify OAuth ---
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

    # Generate the Spotify authorization URL
    auth_url = sp_oauth.get_authorize_url()

    # --- Button to display the Spotify login link ---
    if st.button("Log in to Spotify"):
        st.write("Click below to authorize:")
        st.markdown(f"[**Authorize on Spotify**]({auth_url})")

if __name__ == "__main__":
    main()
