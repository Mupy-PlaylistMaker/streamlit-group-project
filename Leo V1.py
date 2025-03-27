import streamlit as st

# Configure the page
st.set_page_config(page_title="Mupy", layout="centered", page_icon="🎧")

# CSS Styling for the page with updated colors
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
    </style>
""", unsafe_allow_html=True)

# Display the title and login button
st.markdown('<div class="logo-text">Mupy</div>', unsafe_allow_html=True)
st.markdown('<a class="login-btn" href="#">Login</a>', unsafe_allow_html=True)
