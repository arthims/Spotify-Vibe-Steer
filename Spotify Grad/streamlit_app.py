import streamlit as st
import json
import math
import os

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spotify Vibe Steer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS (Spotify Dark Theme) ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Dark background */
    .stApp { background-color: #121212; color: #FFFFFF; }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #282828;
    }
    section[data-testid="stSidebar"] * { color: #FFFFFF !important; }

    /* Main header */
    .main-header {
        background: linear-gradient(135deg, #1DB954 0%, #158a3e 100%);
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .main-header h1 { color: #000 !important; font-size: 28px; font-weight: 800; margin: 0; }
    .main-header p  { color: rgba(0,0,0,0.75) !important; margin: 4px 0 0; font-size: 14px; }

    /* Track cards */
    .track-card {
        background: #181818;
        border: 1px solid #282828;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: background 0.2s;
    }
    .track-card:hover { background: #282828; border-color: #1DB954; }

    .track-rank {
        width: 32px; height: 32px;
        background: #1DB954;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 14px; color: #000;
        flex-shrink: 0;
    }

    .track-name { font-size: 15px; font-weight: 600; color: #FFFFFF; }
    .track-artist { font-size: 13px; color: #B3B3B3; margin-top: 2px; }

    .tag {
        display: inline-block;
        background: rgba(29,185,84,0.15);
        border: 1px solid rgba(29,185,84,0.35);
        color: #1DB954;
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 4px;
        margin-top: 6px;
    }

    /* Chat messages */
    .user-msg {
        background: #1DB954;
        color: #000 !important;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        font-weight: 500;
        max-width: 75%;
        margin-left: auto;
    }
    .bot-msg {
        background: #282828;
        color: #FFF !important;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 85%;
    }
    .explanation-text { color: #E0E0E0; font-size: 14px; line-height: 1.6; margin-bottom: 12px; }

    /* Streamlit overrides */
    .stButton > button {
        background: #1DB954 !important;
        color: #000 !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-size: 14px !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover { background: #1ed760 !important; transform: scale(1.03); }
    .stSelectbox > div > div { background: #181818 !important; border-color: #333 !important; color: #FFF !important; }
    .stTextInput > div > div > input {
        background: #181818 !important;
        border-color: #333 !important;
        color: #FFF !important;
        border-radius: 50px !important;
        padding: 10px 20px !important;
    }
    div[data-testid="stChatInput"] > div { background: #181818 !important; border-color: #1DB954 !important; }
    div[data-testid="stChatMessage"] { background: #181818 !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Embedded Music Catalog ────────────────────────────────────────────────────
CATALOG = [
    {"id":"t1","name":"Senorita","artist":"Yuvan Shankar Raja","language":"Tamil","genre":"Pop","era":"Latest","valence":0.8,"energy":0.9},
    {"id":"t2","name":"Kannaana Kanney","artist":"D. Imman, Sid Sriram","language":"Tamil","genre":"Melody","era":"Latest","valence":0.6,"energy":0.4},
    {"id":"t3","name":"Rowdy Baby","artist":"Dhanush, Dhee","language":"Tamil","genre":"Pop","era":"Latest","valence":0.9,"energy":0.95},
    {"id":"t4","name":"Enjoy Enjaami","artist":"Dhee, Arivu","language":"Tamil","genre":"Folk","era":"Latest","valence":0.85,"energy":0.88},
    {"id":"t5","name":"Kaathuvaakula Rendu Kaadhal","artist":"Anirudh Ravichander","language":"Tamil","genre":"Pop","era":"Latest","valence":0.75,"energy":0.8},
    {"id":"t6","name":"Hukum - Atharva","artist":"Anirudh Ravichander","language":"Tamil","genre":"Pop","era":"Latest","valence":0.88,"energy":0.92},
    {"id":"t7","name":"Naanum Rowdy Dhaan","artist":"Anirudh Ravichander","language":"Tamil","genre":"Pop","era":"Latest","valence":0.87,"energy":0.9},
    {"id":"t8","name":"Kaaval Kaakum","artist":"Sid Sriram","language":"Tamil","genre":"Melody","era":"Latest","valence":0.5,"energy":0.35},
    {"id":"t9","name":"Uyire","artist":"Harris Jayaraj","language":"Tamil","genre":"Melody","era":"Latest","valence":0.55,"energy":0.4},
    {"id":"t10","name":"Roja Theme","artist":"A.R. Rahman","language":"Tamil","genre":"Melody","era":"Old","valence":0.7,"energy":0.4},
    {"id":"t11","name":"Kadhal Rojave","artist":"P. Unnikrishnan, Kavita Krishnamurthy","language":"Tamil","genre":"Melody","era":"Old","valence":0.9,"energy":0.45},
    {"id":"t12","name":"Chinna Chinna Aasai","artist":"Minmini","language":"Tamil","genre":"Folk","era":"Old","valence":0.7,"energy":0.5},
    {"id":"t13","name":"Minsara Kanna","artist":"Nithyasree Mahadevan","language":"Tamil","genre":"Folk","era":"Old","valence":0.65,"energy":0.55},
    {"id":"t14","name":"Pudhu Vellai Mazhai","artist":"Unni Krishnan, Sadhana Sargam","language":"Tamil","genre":"Melody","era":"Old","valence":0.8,"energy":0.5},
    {"id":"t15","name":"Venmathiye","artist":"Sid Sriram","language":"Tamil","genre":"Melody","era":"Old","valence":0.75,"energy":0.42},
    {"id":"m1","name":"Lailakame","artist":"Vineeth Sreenivasan","language":"Malayalam","genre":"Pop","era":"Latest","valence":0.9,"energy":0.8},
    {"id":"m2","name":"Kannil Kannil","artist":"Haricharan, Shreya Ghoshal","language":"Malayalam","genre":"Melody","era":"Latest","valence":0.8,"energy":0.65},
    {"id":"m3","name":"Oru Adaar Love","artist":"Shaasan Ramachandran","language":"Malayalam","genre":"Pop","era":"Latest","valence":0.7,"energy":0.65},
    {"id":"m4","name":"Mizhiyil Ninnum","artist":"Shreya Ghoshal, Najim Arshad","language":"Malayalam","genre":"Melody","era":"Latest","valence":0.6,"energy":0.5},
    {"id":"m5","name":"Theeram","artist":"Arun Gopi","language":"Malayalam","genre":"Melody","era":"Latest","valence":0.8,"energy":0.65},
    {"id":"m6","name":"Mazhaye Mazhaye","artist":"Sid Sriram","language":"Malayalam","genre":"Melody","era":"Latest","valence":0.55,"energy":0.45},
    {"id":"m7","name":"Hey Yaaroda","artist":"Shreya Ghoshal","language":"Malayalam","genre":"Folk","era":"Latest","valence":0.75,"energy":0.7},
    {"id":"m8","name":"Poomaram Title Song","artist":"Alphons Joseph","language":"Malayalam","genre":"Folk","era":"Latest","valence":0.7,"energy":0.65},
    {"id":"m9","name":"Oru Koottil","artist":"MG Sreekumar","language":"Malayalam","genre":"Folk","era":"Old","valence":0.8,"energy":0.6},
    {"id":"m10","name":"Kilukkam Kilukkam","artist":"MG Sreekumar, Kavita Krishnamurthy","language":"Malayalam","genre":"Pop","era":"Old","valence":0.9,"energy":0.85},
    {"id":"m11","name":"Chithram Theme","artist":"KS Chithra, MG Sreekumar","language":"Malayalam","genre":"Melody","era":"Old","valence":0.6,"energy":0.55},
    {"id":"m12","name":"Pramodavanam","artist":"Yesudas","language":"Malayalam","genre":"Melody","era":"Old","valence":0.5,"energy":0.4},
    {"id":"m13","name":"Ponnonam","artist":"Yesudas, KS Chithra","language":"Malayalam","genre":"Folk","era":"Old","valence":0.85,"energy":0.75},
    {"id":"m14","name":"Onnam Vattam Kandappol","artist":"MG Sreekumar","language":"Malayalam","genre":"Melody","era":"Old","valence":0.7,"energy":0.45},
    {"id":"m15","name":"Manjal Prasadavumayi","artist":"Yesudas","language":"Malayalam","genre":"Folk","era":"Old","valence":0.8,"energy":0.6},
    {"id":"h1","name":"Kesariya","artist":"Arijit Singh","language":"Hindi","genre":"Pop","era":"Latest","valence":0.75,"energy":0.7},
    {"id":"h2","name":"Raataan Lambiyan","artist":"Jubin Nautiyal, Asees Kaur","language":"Hindi","genre":"Melody","era":"Latest","valence":0.7,"energy":0.55},
    {"id":"h3","name":"Tum Kab Aoge","artist":"Arijit Singh","language":"Hindi","genre":"Melody","era":"Latest","valence":0.55,"energy":0.4},
    {"id":"h4","name":"Besharam Rang","artist":"Shilpa Rao, Caralisa Monteiro","language":"Hindi","genre":"Pop","era":"Latest","valence":0.9,"energy":0.88},
    {"id":"h5","name":"Chaiyya Chaiyya","artist":"Sukhwinder Singh","language":"Hindi","genre":"Folk","era":"Latest","valence":0.88,"energy":0.9},
    {"id":"h6","name":"Ghungroo","artist":"Arijit Singh, Shilpa Rao","language":"Hindi","genre":"Pop","era":"Latest","valence":0.82,"energy":0.83},
    {"id":"h7","name":"Apna Bana Le","artist":"Arijit Singh","language":"Hindi","genre":"Melody","era":"Latest","valence":0.6,"energy":0.5},
    {"id":"h8","name":"Ve Kamleya","artist":"Arijit Singh, Shreya Ghoshal","language":"Hindi","genre":"Melody","era":"Latest","valence":0.65,"energy":0.55},
    {"id":"h9","name":"Tum Hi Ho","artist":"Arijit Singh","language":"Hindi","genre":"Melody","era":"Old","valence":0.6,"energy":0.45},
    {"id":"h10","name":"Kal Ho Na Ho","artist":"Sonu Nigam","language":"Hindi","genre":"Melody","era":"Old","valence":0.65,"energy":0.5},
    {"id":"h11","name":"Ek Ajnabee Haseena Se","artist":"Kishore Kumar","language":"Hindi","genre":"Pop","era":"Old","valence":0.85,"energy":0.7},
    {"id":"h12","name":"Tere Liye","artist":"Atif Aslam, Shreya Ghoshal","language":"Hindi","genre":"Melody","era":"Old","valence":0.7,"energy":0.5},
    {"id":"h13","name":"Kajra Re","artist":"Alisha Chinai, Shankar Mahadevan","language":"Hindi","genre":"Folk","era":"Old","valence":0.88,"energy":0.85},
    {"id":"h14","name":"Dil Chahta Hai","artist":"Shankar-Ehsaan-Loy","language":"Hindi","genre":"Pop","era":"Old","valence":0.9,"energy":0.85},
    {"id":"h15","name":"Mor Bani Thangat Kare","artist":"Kavita Seth","language":"Hindi","genre":"Folk","era":"Old","valence":0.78,"energy":0.65},
    {"id":"e1","name":"Shape of You","artist":"Ed Sheeran","language":"English","genre":"Pop","era":"Latest","valence":0.93,"energy":0.84},
    {"id":"e2","name":"Blinding Lights","artist":"The Weeknd","language":"English","genre":"Pop","era":"Latest","valence":0.33,"energy":0.8},
    {"id":"e3","name":"As It Was","artist":"Harry Styles","language":"English","genre":"Pop","era":"Latest","valence":0.74,"energy":0.73},
    {"id":"e4","name":"Levitating","artist":"Dua Lipa","language":"English","genre":"Pop","era":"Latest","valence":0.92,"energy":0.82},
    {"id":"e5","name":"Watermelon Sugar","artist":"Harry Styles","language":"English","genre":"Pop","era":"Latest","valence":0.95,"energy":0.82},
    {"id":"e6","name":"Drivers License","artist":"Olivia Rodrigo","language":"English","genre":"Melody","era":"Latest","valence":0.35,"energy":0.35},
    {"id":"e7","name":"Fly Me to the Moon","artist":"Frank Sinatra","language":"English","genre":"Jazz","era":"Old","valence":0.95,"energy":0.55},
    {"id":"e8","name":"What a Wonderful World","artist":"Louis Armstrong","language":"English","genre":"Jazz","era":"Old","valence":0.96,"energy":0.38},
    {"id":"e9","name":"Feeling Good","artist":"Nina Simone","language":"English","genre":"Jazz","era":"Old","valence":0.9,"energy":0.6},
    {"id":"e10","name":"Someone Like You","artist":"Adele","language":"English","genre":"Melody","era":"Old","valence":0.29,"energy":0.36},
    {"id":"e11","name":"Hotel California","artist":"Eagles","language":"English","genre":"Folk","era":"Old","valence":0.66,"energy":0.46},
    {"id":"e12","name":"Blowin In The Wind","artist":"Bob Dylan","language":"English","genre":"Folk","era":"Old","valence":0.55,"energy":0.42},
    {"id":"e13","name":"Take Five","artist":"Dave Brubeck","language":"English","genre":"Jazz","era":"Old","valence":0.88,"energy":0.5},
    {"id":"e14","name":"So What","artist":"Miles Davis","language":"English","genre":"Jazz","era":"Old","valence":0.7,"energy":0.45},
    {"id":"e15","name":"Autumn Leaves","artist":"Miles Davis","language":"English","genre":"Jazz","era":"Old","valence":0.4,"energy":0.35},
    {"id":"te1","name":"Samajavaragamana","artist":"Sid Sriram","language":"Telugu","genre":"Melody","era":"Latest","valence":0.65,"energy":0.5},
    {"id":"te2","name":"Buttabomma","artist":"Armaan Malik","language":"Telugu","genre":"Melody","era":"Latest","valence":0.75,"energy":0.6},
    {"id":"te3","name":"Inkem Inkem Inkem Kaavaale","artist":"Sid Sriram","language":"Telugu","genre":"Melody","era":"Latest","valence":0.55,"energy":0.45},
    {"id":"te4","name":"Oo Antava","artist":"Indravathi Chauhan","language":"Telugu","genre":"Pop","era":"Latest","valence":0.92,"energy":0.9},
    {"id":"te5","name":"Naatu Naatu","artist":"Rahul Sipligunj, Kaala Bhairava","language":"Telugu","genre":"Folk","era":"Latest","valence":0.95,"energy":0.97},
    {"id":"te6","name":"Srivalli","artist":"Sid Sriram","language":"Telugu","genre":"Melody","era":"Latest","valence":0.7,"energy":0.6},
    {"id":"te7","name":"Dhadham Dhadham","artist":"Shreya Ghoshal","language":"Telugu","genre":"Pop","era":"Latest","valence":0.82,"energy":0.78},
    {"id":"te8","name":"Roja Jaaneman","artist":"S.P. Balasubrahmanyam, Lata Mangeshkar","language":"Telugu","genre":"Melody","era":"Old","valence":0.8,"energy":0.45},
    {"id":"te9","name":"Ye Maya Chesave","artist":"A.R. Rahman","language":"Telugu","genre":"Melody","era":"Old","valence":0.6,"energy":0.5},
    {"id":"te10","name":"Manasuna Manasai","artist":"Karthik, Shreya Ghoshal","language":"Telugu","genre":"Melody","era":"Old","valence":0.7,"energy":0.55},
    {"id":"te11","name":"Naatu Naatu (Classic)","artist":"M.M. Keeravani","language":"Telugu","genre":"Folk","era":"Old","valence":0.88,"energy":0.9},
    {"id":"te12","name":"Evare Aatadukunaave","artist":"Sid Sriram","language":"Telugu","genre":"Folk","era":"Latest","valence":0.78,"energy":0.72},
    {"id":"te13","name":"Kolo Kolo","artist":"DSP","language":"Telugu","genre":"Folk","era":"Latest","valence":0.88,"energy":0.9},
    {"id":"te14","name":"Oosupodu","artist":"Anirudh Ravichander","language":"Telugu","genre":"Pop","era":"Latest","valence":0.85,"energy":0.88},
    {"id":"te15","name":"Nakka Mukka","artist":"Karthik","language":"Telugu","genre":"Folk","era":"Old","valence":0.9,"energy":0.87},
]

# ─── Recommendation Engine ─────────────────────────────────────────────────────
MOOD_MAP = {
    "happy":       (0.9, 0.85), "energetic":   (0.8, 0.95),
    "party":       (0.9, 0.95), "dance":       (0.88, 0.9),
    "sad":         (0.2, 0.3),  "heartbreak":  (0.2, 0.35),
    "chill":       (0.6, 0.35), "relax":       (0.65, 0.3),
    "romantic":    (0.75, 0.45),"love":        (0.78, 0.5),
    "workout":     (0.8, 0.95), "focus":       (0.5, 0.4),
    "sleep":       (0.5, 0.2),  "morning":     (0.8, 0.65),
    "night":       (0.4, 0.35), "motivational":(0.85, 0.9),
    "melancholic": (0.3, 0.3),  "nostalgic":   (0.6, 0.4),
}

def parse_mood(text):
    lower = text.lower()
    for kw, (v, e) in MOOD_MAP.items():
        if kw in lower:
            return v, e
    return 0.6, 0.6

def parse_intent(text):
    lower = text.lower()
    lang, genre, era = "", "", ""
    if "tamil" in lower:        lang = "Tamil"
    elif "malayalam" in lower:  lang = "Malayalam"
    elif "hindi" in lower:      lang = "Hindi"
    elif "telugu" in lower:     lang = "Telugu"
    elif "english" in lower:    lang = "English"
    if "jazz" in lower:         genre = "Jazz"
    elif "folk" in lower:       genre = "Folk"
    elif any(w in lower for w in ["melody","melodic","soft"]): genre = "Melody"
    elif "pop" in lower:        genre = "Pop"
    if any(w in lower for w in ["latest","new","recent","2020","2024","2023","2022"]): era = "Latest"
    elif any(w in lower for w in ["old","classic","retro","vintage","90s","80s"]):    era = "Old"
    return lang, genre, era

def recommend(text, filter_lang, filter_genre, filter_era):
    t_lang, t_genre, t_era = parse_intent(text)
    lang  = filter_lang  or t_lang
    genre = filter_genre or t_genre
    era   = filter_era   or t_era
    val, nrg = parse_mood(text)

    pool = [t for t in CATALOG
            if (not lang  or t["language"].lower() == lang.lower())
            and (not genre or t["genre"].lower()    == genre.lower())
            and (not era   or t["era"].lower()      == era.lower())]

    # Fallback: relax era → relax genre → use all
    if len(pool) < 3 and era:
        pool = [t for t in CATALOG
                if (not lang  or t["language"].lower() == lang.lower())
                and (not genre or t["genre"].lower()   == genre.lower())]
    if len(pool) < 3:
        pool = [t for t in CATALOG if not lang or t["language"].lower() == lang.lower()]
    if not pool:
        pool = CATALOG

    scored = sorted(pool, key=lambda t: math.sqrt((t["valence"]-val)**2 + (t["energy"]-nrg)**2))
    return scored[:3], lang, genre, era, val, nrg

def mood_label(val, nrg):
    if val > 0.8 and nrg > 0.8:   return "upbeat & energetic 🎉"
    if val > 0.7 and nrg < 0.5:   return "warm & romantic 💫"
    if val < 0.4 and nrg < 0.4:   return "melancholic & soft 🌧️"
    if nrg > 0.85:                 return "high energy 🔥"
    if val > 0.7:                  return "happy & positive ✨"
    return "balanced & mellow 🎶"

# ─── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trigger" not in st.session_state:
    st.session_state.trigger = None

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    col_logo, col_title = st.columns([1, 4])
    with col_logo:
        st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg", width=40)
    with col_title:
        st.markdown("### Spotify Vibe Steer")

    st.markdown("---")
    st.markdown("**🎛️ Recommendation Filters**")
    st.caption("Pinpoint the perfect top 3 songs for you")

    sel_lang  = st.selectbox("🌐 Language",    ["Any", "Tamil", "Malayalam", "Hindi", "English", "Telugu"])
    sel_genre = st.selectbox("🎸 Genre",       ["Any", "Pop", "Folk", "Jazz", "Melody"])
    sel_era   = st.selectbox("🕐 Time Period", ["Any", "Latest (2020s)", "Classic / Old"])

    era_map = {"Any": "", "Latest (2020s)": "Latest", "Classic / Old": "Old"}
    f_lang  = "" if sel_lang  == "Any" else sel_lang
    f_genre = "" if sel_genre == "Any" else sel_genre
    f_era   = era_map[sel_era]

    st.markdown("---")
    st.markdown("**⚡ Quick Categories**")

    PILLS = [
        ("🎵 Latest Tamil",    "Tamil",    "",       "Latest"),
        ("🎵 Latest Malayalam","Malayalam","",       "Latest"),
        ("🎵 Latest Hindi",    "Hindi",    "",       "Latest"),
        ("🎵 Latest English",  "English",  "",       "Latest"),
        ("🎵 Latest Telugu",   "Telugu",   "",       "Latest"),
        ("🎷 Jazz",            "English",  "Jazz",   ""),
        ("🎤 Pop",             "",         "Pop",    ""),
        ("🪗 Folk",            "",         "Folk",   ""),
        ("🎼 Melody",          "",         "Melody", ""),
        ("🪗 Folk Hindi",      "Hindi",    "Folk",   ""),
        ("🪗 Folk Tamil",      "Tamil",    "Folk",   ""),
        ("🪗 Folk Malayalam",  "Malayalam","Folk",   ""),
        ("🪗 Folk English",    "English",  "Folk",   ""),
        ("🪗 Folk Telugu",     "Telugu",   "Folk",   ""),
        ("🎼 Melody Tamil",    "Tamil",    "Melody", ""),
        ("🎼 Melody Telugu",   "Telugu",   "Melody", ""),
        ("🎼 Melody Malayalam","Malayalam","Melody", ""),
        ("🎼 Melody Hindi",    "Hindi",    "Melody", ""),
        ("🎼 Melody English",  "English",  "Melody", ""),
    ]

    cols = st.columns(2)
    for i, (label, lang, genre, era) in enumerate(PILLS):
        with cols[i % 2]:
            if st.button(label, key=f"pill_{i}", use_container_width=True):
                parts = [x for x in [era.lower() if era else "", lang, genre.lower() if genre else ""] if x]
                auto_text = f"Recommend me {' '.join(parts)} songs"
                st.session_state.trigger = (auto_text, lang, genre, era)

    st.markdown("---")
    if st.button("🎵 Recommend for Me", use_container_width=True, key="main_recommend"):
        parts = [x for x in [f_era.lower() if f_era else "", f_lang, f_genre.lower() if f_genre else ""] if x]
        auto_text = f"Recommend me {' '.join(parts) if parts else 'great'} songs"
        st.session_state.trigger = (auto_text, f_lang, f_genre, f_era)

# Helper function to process recommendation request and append directly to session history
def run_and_append_message(user_text, lang, genre, era):
    st.session_state.messages.append({"role": "user", "content": user_text})
    tracks, r_lang, r_genre, r_era, val, nrg = recommend(user_text, lang, genre, era)

    filters = " · ".join(f for f in [r_lang, r_genre, r_era] if f)
    filter_line = f"**Filters:** {filters}  |  " if filters else ""
    intro = f"{filter_line}**Vibe detected:** {mood_label(val, nrg)}\n\nHere are your **Top 3 Picks** 🎶"

    cards_html = ""
    for i, t in enumerate(tracks, 1):
        cards_html += f"""
        <div class="track-card">
          <div class="track-rank">{i}</div>
          <div style="flex:1">
            <div class="track-name">{t['name']}</div>
            <div class="track-artist">{t['artist']}</div>
            <div>
              <span class="tag">{t['language']}</span>
              <span class="tag">{t['genre']}</span>
              <span class="tag">{t['era']}</span>
            </div>
          </div>
          <div style="font-size:24px">🎵</div>
        </div>"""

    full_response = f"{intro}\n\n{cards_html}"
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ─── Main Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" width="44"/>
  <div>
    <h1>Spotify Vibe Steer</h1>
    <p>Tell me your mood — I'll find the perfect top 3 tracks for you</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Tabs Setup (Phase 6 implementation) ──────────────────────────────────────
tab1, tab2 = st.tabs(["💬 Vibe Steer Chat", "📊 Review Discovery Analytics"])

with tab1:
    # Welcome message (first load only)
    if not st.session_state.messages:
        st.info("👋 Hi! I'm your **AI Music Curator**. Type your mood below or use the sidebar filters. Try: *'I want chill Tamil melodies'* or *'Give me energetic Hindi songs'*")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="🎵" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"], unsafe_allow_html=True)

    # Handle sidebar trigger (pill or recommend button)
    if st.session_state.trigger:
        txt, lg, gn, er = st.session_state.trigger
        st.session_state.trigger = None
        run_and_append_message(txt, lg, gn, er)
        st.rerun()

    # Handle chat input
    prompt = st.chat_input("Type your mood or song request… e.g. 'I want happy Tamil pop songs'")
    if prompt:
        run_and_append_message(prompt, f_lang, f_genre, f_era)
        st.rerun()

with tab2:
    st.markdown("### 📊 Qualitative Review Analytics")
    st.caption("Analyzing user complaints, frustrations, and unmet needs focused on Music Discovery & Repetitive Loops.")
    
    import pandas as pd
    
    csv_path = "Reviews_Spotify_Discovery_Filtered.csv"
    # Fallback to absolute path if running from parent context
    if not os.path.exists(csv_path):
        csv_path = r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify_Discovery_Filtered.csv"
        
    if os.path.exists(csv_path):
        df_filtered = pd.read_csv(csv_path)
        
        # 1. Metric Row (Focused strictly on discovery-relevant reviews)
        st.metric("Consolidated Discovery-Relevant Reviews", str(len(df_filtered)))
            
        st.markdown("---")
        
        # 2. Charts Row
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown("#### 📱 Discovery Feedback by Platform")
            # Count by Platform
            plat_counts = df_filtered["Platform"].value_counts().reset_index()
            plat_counts.columns = ["Platform", "Reviews"]
            st.bar_chart(plat_counts.set_index("Platform"))
            
        with c_col2:
            st.markdown("#### ⭐ Rating Distribution (App/Play Store)")
            # Rating counts for reviews that have ratings
            df_rated = df_filtered[df_filtered["Rating"].notna()]
            if not df_rated.empty:
                # Convert rating to integer categories
                df_rated["Rating"] = df_rated["Rating"].astype(int)
                rating_counts = df_rated["Rating"].value_counts().sort_index().reset_index()
                rating_counts.columns = ["Stars", "Reviews"]
                st.bar_chart(rating_counts.set_index("Stars"))
            else:
                st.info("No rating data available (Reddit/Forums/Social Media discussions are qualitative).")
                
        st.markdown("---")
        
        # 3. Predefined Problem Explorer & Search
        st.markdown("#### 🔍 Interactive Review Explorer")
        
        # Select predefined topics
        topic_options = {
            "All Relevant Reviews": [],
            "Smart Shuffle & Rec Loops": ["shuffle", "smart shuffle", "repeat", "same", "loop"],
            "UI/UX Curation Changes (Heart Button, Widgets)": ["heart", "plus", "widget", "layout", "button"],
            "Content Clutter (Podcasts/Audiobooks)": ["podcast", "audiobook", "show", "bloat"],
            "Ads & Curation Restraints (Free Tier)": ["ads", "ad", "free", "premium", "paywall"]
        }
        
        sel_topic = st.selectbox("🎯 Filter by Problem Topic", list(topic_options.keys()))
        search_kw = st.text_input("🔍 Or search custom keywords (e.g. 'carplay', 'lyrics', 'slow'):").strip().lower()
        
        # Apply filters
        df_display = df_filtered.copy()
        
        # Predefined keywords
        keywords_to_filter = topic_options[sel_topic]
        if keywords_to_filter:
            df_display = df_display[df_display["Review_Text"].str.lower().str.contains('|'.join(keywords_to_filter), na=False)]
            
        # Custom keyword
        if search_kw:
            df_display = df_display[df_display["Review_Text"].str.lower().str.contains(search_kw, na=False)]
            
        st.caption(f"Showing {len(df_display)} matching reviews out of {len(df_filtered)}")
        
        # Display as cards
        for idx, row in df_display.head(20).iterrows():
            stars_badge = f"⭐ {int(row['Rating'])} Stars" if pd.notna(row['Rating']) else "💬 Discussion"
            plat_badge = row['Platform']
            st.markdown(f"""
            <div style="background:#181818; border: 1px solid #282828; padding:12px 16px; border-radius:8px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:12px; color:#1DB954; font-weight:600;">{plat_badge}</span>
                    <span style="font-size:12px; color:#B3B3B3;">{stars_badge}</span>
                </div>
                <div style="font-size:13px; color:#FFFFFF; line-height:1.4;">"{row['Review_Text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            

            
    else:
        st.warning(f"Could not load review analytics. Please make sure the consolidated file exists at {csv_path}")

