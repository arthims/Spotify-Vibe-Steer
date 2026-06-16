import streamlit as st
import requests
import os

st.set_page_config(page_title="Spotify Vibe Steer", page_icon="🎵", layout="wide")

col1, col2 = st.columns([9, 1])
with col1:
    st.title("🎵 Spotify Vibe Steer")
with col2:
    st.image("https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_CMYK_Green.png", width=100)

st.markdown("A conversational AI assistant that translates your exact mood into music recommendations.")

with st.sidebar:
    st.header("Recommendations Filters")
    st.markdown("Help us accurately recommend the top 3 songs for you by selecting your preferences below:")
    sel_lang = st.selectbox("Language", ["Any", "English", "Hindi", "Tamil", "Telugu", "Malayalam"])
    sel_genre = st.selectbox("Genre", ["Any", "Pop", "Folk", "Jazz", "Melody"])
    sel_era = st.selectbox("Time Period", ["Any", "Latest", "Old"])
    
    st.markdown("---")
    # The Recommend Button
    if st.button("Recommend", use_container_width=True):
        st.session_state.trigger_recommend = True

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm your AI Music Curator. Tell me what you want to hear right now. You can also use the filters on the left and click 'Recommend'!"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if triggered by sidebar button or by chat input
prompt = st.chat_input("I want to listen to...")
is_button_triggered = st.session_state.get("trigger_recommend", False)

if prompt or is_button_triggered:
    # Reset the trigger
    st.session_state.trigger_recommend = False
    
    user_msg = prompt if prompt else f"Recommend me {sel_era if sel_era != 'Any' else ''} {sel_lang if sel_lang != 'Any' else ''} {sel_genre if sel_genre != 'Any' else ''} songs."
    
    st.session_state.messages.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing intent and steering the algorithm..."):
            try:
                payload = {
                    "user_prompt": user_msg,
                    "language": sel_lang if sel_lang != "Any" else None,
                    "genre": sel_genre if sel_genre != "Any" else None,
                    "era": sel_era if sel_era != "Any" else None
                }
                BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
                res = requests.post(f"{BACKEND_URL}/chat", json=payload)
                if res.status_code == 200:
                    data = res.json()
                    tracks = data.get("tracks", [])
                    explanation = data.get("explanation", "")
                    
                    response_content = f"**AI Curator:** {explanation}\n\n### Recommended Tracks:\n"
                    for i, t in enumerate(tracks, 1):
                        response_content += f"{i}. **{t['name']}** by {t['artist']} *(Language: {t['language']}, Genre: {t['genre'].capitalize()}, Era: {t['era'].capitalize()})*\n"
                    
                    st.markdown(response_content)
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                else:
                    st.error(f"Backend Error: {res.text}")
            except Exception as e:
                st.error("Could not connect to the backend. Is FastAPI running on port 8000?")
