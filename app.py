import streamlit as st
import streamlit.components.v1 as components
import os

# Set page config for wide layout and Spotify title
st.set_page_config(
    page_title="Spotify AI Loop Breaker",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit header, footer and default margins using CSS injection
hide_style = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
        iframe {
            border: none !important;
        }
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# Path to our high-fidelity frontend player HTML file
html_path = os.path.join(os.path.dirname(__file__), "frontend_web", "index.html")

# Read the HTML content
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Render the HTML player taking the entire viewport
    components.html(html_content, height=950, scrolling=True)
else:
    st.error("Frontend HTML player file not found! Please check repository files.")
