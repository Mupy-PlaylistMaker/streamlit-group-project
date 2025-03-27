import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "dcfd782b75b4472c9712492560b7a142"
CLIENT_SECRET = "01a88c106a204ca1a4f819e0f73d0ffa"
REDIRECT_URI = "https://spotify20app-bbgh7fg7susxwuu26hpwis.streamlit.app/"
SCOPE = "user-library-read playlist-modify-private"

def main():
    st.title("MUPY")
    
    # Initialize Spotipy OAuth
    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )
    
    # Check if we have a stored token
    if "access_token" not in st.session_state:
        # If not logged in, show a login button
        if st.button("Log in with Spotify"):
            auth_url = sp_oauth.get_authorize_url()
            st.write("Click below to authorize:")
            st.markdown(f"[**Authorize on Spotify**]({auth_url})")
        
        # If user is coming back from Spotify with the ?code= param
        query_params = st.query_params
        if "code" in query_params:
            code = query_params["code"][0]
            token_info = sp_oauth.get_access_token(code)
            if token_info:
                st.session_state["access_token"] = token_info["access_token"]
                st.success("Logged in successfully!")
                st.experimental_rerun()
    else:
        # Already have a token, create Spotify client
        sp = spotipy.Spotify(auth=st.session_state["access_token"])
        
        # Example: Show user’s profile
        user_info = sp.current_user()
        st.write("Welcome 🎧")
        st.write(f"**Name:** {user_info['display_name']}")
        st.write(f"**Email:** {user_info['email']}")
        st.write(f"**Country:** {user_info['country']}")
        
        # LOGOUT BUTTON
        if st.button("Logout"):
            # Clear the token from session_state
            st.session_state.pop("access_token", None)
            st.success("You have been logged out.")
            st.experimental_rerun()  # Refresh so the app re-checks login state

if __name__ == "__main__":
    main()
