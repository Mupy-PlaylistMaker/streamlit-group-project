import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- Spotify Credentials ---
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "http://localhost:8501/callback"  # Updated Redirect URI
SCOPE = "user-read-private user-read-email user-library-read"

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
)

# --- Page Setup ---
st.set_page_config(page_title="MUPY", layout="centered", page_icon="🎧")

# --- UI Content ---
st.title("🎧 MUPY")

# Handle login redirect
query_params = st.query_params
if "code" in query_params:
    try:
        token_info = sp_oauth.get_access_token(query_params["code"])
        st.session_state["token_info"] = token_info
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

# Display login or user information
if "token_info" not in st.session_state:
    auth_url = sp_oauth.get_authorize_url()
    st.markdown(f"[Log in with Spotify]({auth_url})")
else:
    sp = spotipy.Spotify(auth=st.session_state["token_info"]["access_token"])
    user = sp.current_user()

    st.success("✅ Logged in successfully!")
    st.subheader("Welcome 🎧")
    st.write(f"Name: {user['display_name']}")
    st.write(f"Email: {user['email']}")
    st.write(f"Country: {user['country']}")
    if user["images"]:
        st.image(user["images"][0]["url"], width=150)
