import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time

# --- Spotify Credentials ---
CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "https://spotify20appleopy-wr6jzbaagwn9sxdzmtmjwl.streamlit.app/"
SCOPE = "user-read-private user-read-email"

# --- Streamlit Setup ---
st.set_page_config(page_title="MUPY", layout="centered")
st.title("🎧 MUPY - Debug Login")

# --- OAuth Config ---
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache-mupy"
)

# --- Get auth URL ---
auth_url = sp_oauth.get_authorize_url()
query_params = st.query_params

# --- Helper: reset session
def clear_session_and_reload():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_set_query_params()  # Clear URL
    st.warning("Session reset. Please try logging in again.")
    st.stop()

# --- DEBUG BLOCK ---
st.subheader("🛠 Debug Info")
st.write("Session state:", st.session_state)
st.write("Query params:", query_params)

# --- Handle redirect from Spotify ---
if "code" in query_params:
    code = query_params.get("code")[0]
    st.info(f"Received code: `{code}`")
    
    try:
        token_info = sp_oauth.get_access_token(code, as_dict=False)
        if token_info:
            st.success("✅ Access token retrieved!")
            st.session_state['token_info'] = token_info
            st.experimental_set_query_params()  # Clear ?code from URL
            st.rerun()
        else:
            st.error("⚠️ Token info was empty.")
            clear_session_and_reload()

    except spotipy.SpotifyOauthError as oauth_error:
        st.error("❌ SpotifyOAuthError: Invalid or expired code.")
        st.exception(oauth_error)
        clear_session_and_reload()

    except Exception as e:
        st.error("❌ Unknown error during token exchange.")
        st.exception(e)
        clear_session_and_reload()

# --- Pre-login screen ---
if "token_info" not in st.session_state:
    st.subheader("🔒 Log in with Spotify")
    st.markdown(f"[👉 Click here to log in with Spotify]({auth_url})", unsafe_allow_html=True)
    st.stop()

# --- Post-login UI ---
try:
    sp = spotipy.Spotify(auth=st.session_state['token_info']['access_token'])
    user = sp.current_user()

    st.success("🎉 You are logged in!")
    st.write("**Display Name:**", user.get("display_name"))
    st.write("**Email:**", user.get("email"))
    st.write("**Country:**", user.get("country"))

    if user.get("images"):
        st.image(user["images"][0]["url"], width=120)

    if st.button("🚪 Log Out"):
        clear_session_and_reload()

except Exception as e:
    st.error("⚠️ Failed to fetch user profile.")
    st.exception(e)
    clear_session_and_reload()
