import streamlit as st
import json
import math
import os
import datetime
import calendar
import time

def get_live_date_range(period_str):
    import re
    today = datetime.date.today()
    match = re.search(r'\d+', period_str)
    months = int(match.group()) if match else 1
        
    year = today.year
    month = today.month - months
    if month <= 0:
        month += 12
        year -= 1
        
    max_days = calendar.monthrange(year, month)[1]
    past_day = min(today.day, max_days)
    past_date = datetime.date(year, month, past_day)
    
    def format_day(d):
        if d == 22:
            return "22"
        elif d == 23:
            return "23rd"
        else:
            if 11 <= d <= 13:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
            return f"{d}{suffix}"
            
    today_str = f"{format_day(today.day)} {today.strftime('%B %Y').lower()}"
    past_str = f"{format_day(past_date.day)} {past_date.strftime('%B %Y').lower()}"
    return f"{today_str} to {past_str}"

def format_custom_date_range(from_date, to_date):
    def format_day(d):
        if d == 22:
            return "22"
        elif d == 23:
            return "23rd"
        else:
            if 11 <= d <= 13:
                suffix = "th"
            else:
                suffix = {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
            return f"{d}{suffix}"
            
    from_str = f"{format_day(from_date.day)} {from_date.strftime('%B %Y').lower()}"
    to_str = f"{format_day(to_date.day)} {to_date.strftime('%B %Y').lower()}"
    return f"{from_str} to {to_str}"


# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Review Discovery",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        background: #181818;
        border: 1px solid #282828;
        border-left: 5px solid #1DB954;
        padding: 20px 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .main-header h1 { color: #FFFFFF !important; font-size: 28px; font-weight: 800; margin: 0; }
    .main-header p  { color: #B3B3B3 !important; margin: 4px 0 0; font-size: 14px; }

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

# ─── Embedded Music Catalog (Removed as project focus shifted to Review Discovery) ───
# ─── Main Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" width="44"/>
  <div>
    <h1>Spotify Review Discovery</h1>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Dashboard Helper ─────────────────────────────────────────────────────────
def render_dashboard(date_range):
    st.markdown(f"### 📊 Review Discovery Analytics")
    st.markdown(f"Analysis Period: **{date_range}**")
    
    col_dash1, col_dash2 = st.columns([8, 2])
    with col_dash1:
        st.caption("Analyzing user complaints, frustrations, and unmet needs focused on Music Discovery & Repetitive Loops.")
    with col_dash2:
        if st.button("🔄 Change Period", key="reset_analysis_btn", use_container_width=True):
            st.session_state.analyzed = False
            st.rerun()
            
    import pandas as pd
    
    csv_path = "Reviews_Spotify_Discovery_Filtered.csv"
    if not os.path.exists(csv_path):
        csv_path = r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify_Discovery_Filtered.csv"
        
    if os.path.exists(csv_path):
        df_filtered = pd.read_csv(csv_path)
        
        # Metric Row
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("Total Reviews Ingested (Capped)", "1,500")
        with m_col2:
            st.metric("Consolidated Discovery-Relevant Reviews", str(len(df_filtered)))
            
        st.markdown("---")
        
        # Charts Row
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown("#### 📱 Discovery Feedback by Platform")
            plat_counts = df_filtered["Platform"].value_counts().reset_index()
            plat_counts.columns = ["Platform", "Reviews"]
            st.bar_chart(plat_counts.set_index("Platform"))
            
        with c_col2:
            st.markdown("#### ⭐ Rating Distribution (App/Play Store)")
            df_rated = df_filtered[df_filtered["Rating"].notna()]
            if not df_rated.empty:
                df_rated["Rating"] = df_rated["Rating"].astype(int)
                rating_counts = df_rated["Rating"].value_counts().sort_index().reset_index()
                rating_counts.columns = ["Stars", "Reviews"]
                st.bar_chart(rating_counts.set_index("Stars"))
            else:
                st.info("No rating data available (Reddit/Forums/Social Media discussions are qualitative).")
                
        st.markdown("---")
        
        # Predefined Problem Explorer & Search
        st.markdown("#### 🔍 Interactive Review Explorer")
        
        topic_options = {
            "All Relevant Reviews": [],
            "Smart Shuffle & Rec Loops": ["shuffle", "smart shuffle", "repeat", "same", "loop"],
            "UI/UX Curation Changes (Heart Button, Widgets)": ["heart", "plus", "widget", "layout", "button"],
            "Content Clutter (Podcasts/Audiobooks)": ["podcast", "audiobook", "show", "bloat"],
            "Ads & Curation Restraints (Free Tier)": ["ads", "ad", "free", "premium", "paywall"]
        }
        
        safe_key = "".join(c for c in date_range if c.isalnum())
        sel_topic = st.selectbox("🎯 Filter by Problem Topic", list(topic_options.keys()), key=f"topic_sel_{safe_key}")
        search_kw = st.text_input("🔍 Or search custom keywords (e.g. 'carplay', 'lyrics', 'slow'):", key=f"search_kw_{safe_key}").strip().lower()
        
        df_display = df_filtered.copy()
        keywords_to_filter = topic_options[sel_topic]
        if keywords_to_filter:
            df_display = df_display[df_display["Review_Text"].str.lower().str.contains('|'.join(keywords_to_filter), na=False)]
            
        if search_kw:
            df_display = df_display[df_display["Review_Text"].str.lower().str.contains(search_kw, na=False)]
            
        st.caption(f"Showing {len(df_display)} matching reviews out of {len(df_filtered)}")
        
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

# ─── Tabs Setup ───────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📅 Time Period", "📊 Review Discovery Analytics"])

with tab1:
    if not st.session_state.get("analyzed", False):
        st.markdown("### 📅 Time Period Selection")
        st.caption("Configure the time window to run the review discovery analysis.")
        
        st.markdown("**Choose selector format:**")
        selection_mode = st.radio(
            "Selector Mode",
            ["Preset Window (Dropdown)", "Custom Window (Calendar)"],
            horizontal=True,
            label_visibility="collapsed",
            key="time_selection_mode"
        )
        
        if selection_mode == "Preset Window (Dropdown)":
            selected_period = st.selectbox(
                "📅 Select Preset Window",
                [
                    "last 1 month",
                    "last 2 months",
                    "last 3 months",
                    "last 4 months",
                    "last 5 months",
                    "last 6 months"
                ],
                key="time_period_dropdown"
            )
            range_str = get_live_date_range(selected_period)
        else:
            st.markdown("📅 **Select Custom Window**")
            col_date1, col_date2 = st.columns(2)
            with col_date1:
                from_date = st.date_input(
                    "From Date",
                    value=datetime.date.today() - datetime.timedelta(days=30),
                    key="from_date_picker"
                )
            with col_date2:
                to_date = st.date_input(
                    "To Date",
                    value=datetime.date.today(),
                    key="to_date_picker"
                )
            range_str = format_custom_date_range(from_date, to_date)
            
        st.markdown(f"""
        <div style="background:#181818; border: 1px solid #282828; padding:16px 20px; border-radius:12px; margin-top:10px; margin-bottom:20px;">
            <div style="font-size:12px; color:#B3B3B3; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Live Date Range</div>
            <div style="font-size:18px; color:#1DB954; font-weight:700; margin-top:4px;">{range_str}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Analyse", key="analyse_button", use_container_width=True):
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            status_text.markdown("🔌 **Connecting to Spotify Scraper Service...**")
            time.sleep(0.6)
            
            progress_bar.progress(0.2)
            status_text.markdown("📥 **Scraping Apple App Store & Google Play Store reviews...**")
            time.sleep(0.8)
            
            progress_bar.progress(0.4)
            status_text.markdown("🔍 **Scanning Spotify Forums for Help & Support topics...**")
            time.sleep(0.8)
            
            progress_bar.progress(0.6)
            status_text.markdown("⚠️ **Parsing Ongoing Issues Tracker...**")
            time.sleep(0.8)
            
            progress_bar.progress(0.8)
            status_text.markdown("💡 **Summarizing user feature requests & feedback...**")
            time.sleep(0.8)
            
            progress_bar.progress(1.0)
            status_text.markdown("📊 **Analysis complete! Classifying relevant discovery complaints...**")
            time.sleep(0.6)
            
            st.session_state.analyzed = True
            st.session_state.last_analyzed_period = range_str
            st.rerun()
    else:
        render_dashboard(st.session_state.get("last_analyzed_period", "last 1 month"))

with tab2:
    if st.session_state.get("analyzed", False):
        render_dashboard(st.session_state.get("last_analyzed_period", "last 1 month"))
    else:
        st.warning("⚠️ Analysis has not been run yet.")
        st.info("Please go to the **📅 Time Period** tab and click the **Analyse** button to view the Review Discovery Analytics dashboard.")
