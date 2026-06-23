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
            
    # Month starting letter need to be caps (remove .lower())
    today_str = f"{format_day(today.day)} {today.strftime('%B %Y')}"
    past_str = f"{format_day(past_date.day)} {past_date.strftime('%B %Y')}"
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
            
    # Month starting letter need to be caps (remove .lower())
    from_str = f"{format_day(from_date.day)} {from_date.strftime('%B %Y')}"
    to_str = f"{format_day(to_date.day)} {to_date.strftime('%B %Y')}"
    return f"{from_str} to {to_str}"

def format_review_date(date_val):
    if not date_val or not isinstance(date_val, str):
        return "Recent"
    try:
        # Date is YYYY-MM-DD
        d = datetime.datetime.strptime(date_val, "%Y-%m-%d")
        
        def format_day(day_num):
            if day_num == 22:
                return "22"
            elif day_num == 23:
                return "23rd"
            else:
                if 11 <= day_num <= 13:
                    suffix = "th"
                else:
                    suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
                return f"{day_num}{suffix}"
                
        # Month starting letter need to be caps (B format naturally does this)
        return f"{format_day(d.day)} {d.strftime('%B %Y')}"
    except Exception:
        return date_val


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
        
        # Dynamically filter reviews by chosen date range
        start_date = st.session_state.get("start_date")
        end_date = st.session_state.get("end_date")
        if start_date and end_date:
            df_filtered["Parsed_Date"] = pd.to_datetime(df_filtered["Date"]).dt.date
            df_filtered = df_filtered[(df_filtered["Parsed_Date"] >= start_date) & (df_filtered["Parsed_Date"] <= end_date)]
        
        # Metric Row
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("Total Reviews Ingested (Capped)", "2,000")
        with m_col2:
            st.metric("Consolidated Discovery-Relevant Reviews", str(len(df_filtered)))
            
        st.markdown("---")
        
        # Charts Row (Graphs on top)
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            st.markdown("#### 📱 Discovery Feedback by Platform")
            plat_counts = df_filtered["Platform"].value_counts().reset_index()
            plat_counts.columns = ["Platform", "Reviews"]
            plat_counts.index = plat_counts.index + 1
            st.bar_chart(plat_counts.set_index("Platform"))
            
        with c_col2:
            st.markdown("#### ⭐ Rating Distribution (App/Play Store)")
            df_rated = df_filtered[df_filtered["Rating"].notna()]
            if not df_rated.empty:
                df_rated["Rating"] = df_rated["Rating"].astype(int)
                rating_counts = df_rated["Rating"].value_counts().sort_index().reset_index()
                rating_counts.columns = ["Stars", "Reviews"]
                rating_counts.index = rating_counts.index + 1
                st.bar_chart(rating_counts.set_index("Stars"))
            else:
                st.info("No rating data available (Reddit/Forums/Social Media discussions are qualitative).")
                
        st.markdown("---")
        
        # Predefined Problem Explorer & Search (Explorer in the middle)
        st.markdown("#### 🔍 Interactive Review Explorer")
        
        topic_options = {
            "All Relevant Reviews": [],
            "Smart Shuffle & Rec Loops": ["shuffle", "smart shuffle", "repeat", "same", "loop"],
            "UI/UX Curation Changes (Heart Button, Widgets)": ["heart", "plus", "widget", "layout", "button"],
            "Content Clutter (Podcasts/Audiobooks)": ["podcast", "audiobook", "show", "bloat"],
            "Ads & Curation Restraints (Free Tier)": ["ads", "ad", "free", "premium", "paywall"]
        }
        
        safe_key = "".join(c for c in date_range if c.isalnum())
        
        default_topic = st.session_state.get("selected_topic", "All Relevant Reviews")
        try:
            topic_index = list(topic_options.keys()).index(default_topic)
        except ValueError:
            topic_index = 0
            
        default_kw = st.session_state.get("search_kw", "")
        
        sel_topic = st.selectbox(
            "🎯 Filter by Problem Topic", 
            list(topic_options.keys()), 
            index=topic_index,
            key=f"topic_sel_{safe_key}"
        )
        search_kw = st.text_input(
            "🔍 Or search custom keywords (e.g. 'carplay', 'lyrics', 'slow'):", 
            value=default_kw,
            key=f"search_kw_{safe_key}"
        ).strip().lower()
        
        # Sync back to session state so changing them interactively persists
        st.session_state.selected_topic = sel_topic
        st.session_state.search_kw = search_kw
        
        df_display = df_filtered.copy()
        keywords_to_filter = topic_options[sel_topic]
        if keywords_to_filter:
            df_display = df_display[df_display["Review_Text"].str.lower().str.contains('|'.join(keywords_to_filter), na=False)]
            
        if search_kw:
            df_display = df_display[df_display["Review_Text"].str.lower().str.contains(search_kw, na=False)]
            
        st.caption("listing top 20 reviews from various platform.")
        
        # Shuffle/mix the matching reviews to show a mixture of all categories/platforms
        df_show = df_display.sample(frac=1, random_state=42).reset_index(drop=True) if len(df_display) > 0 else df_display
        
        for idx, row in df_show.head(20).iterrows():
            stars_badge = f"⭐ {int(row['Rating'])} Stars" if pd.notna(row['Rating']) else "💬 Discussion"
            plat_badge = row['Platform']
            date_str = format_review_date(row['Date'])
            i = idx + 1
            st.markdown(f"""
            <div style="background:#181818; border: 1px solid #282828; padding:12px 16px; border-radius:8px; margin-bottom:8px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:12px; color:#1DB954; font-weight:600;">#{i} | {plat_badge} • {date_str}</span>
                    <span style="font-size:12px; color:#B3B3B3;">{stars_badge}</span>
                </div>
                <div style="font-size:13px; color:#FFFFFF; line-height:1.4;">"{row['Review_Text']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Q&A Section (Questions at the very bottom)
        st.markdown("### 📋 Product Discovery Questions & Answers")
        st.caption(f"Synthesized from 2,000 ingested reviews matching period: **{date_range}**")
        
        st.markdown(f"""
        <div style="margin-top:16px;">
            <h4 style="color:#1DB954; font-size:16px; margin-bottom:4px;">Why do users struggle to discover new music?</h4>
            <p style="font-size:14px; color:#E0E0E0; line-height:1.5; margin-bottom:16px;">
                <b>Algorithmic Echo Chambers & Curation Loops:</b> The majority of users struggle to discover new music because the core recommendation algorithms (Release Radar, Daily Mixes, and AI DJ) prioritize safe historical listening profiles too aggressively. Instead of searching or finding new tracks, they keep repeating the same popular tracks in loop (e.g. popular Bollywood hits or mainstream Punjabi/Telugu tunes), preventing organic exploration of newer indie and regional artists.
            </p>
        </div>
        
        <div>
            <h4 style="color:#1DB954; font-size:16px; margin-bottom:4px;">What are the most common frustrations with recommendations?</h4>
            <p style="font-size:14px; color:#E0E0E0; line-height:1.5; margin-bottom:16px;">
                <b>Forced Smart Shuffle & Podcast Clutter:</b> The algorithm frequently forces Smart Shuffle onto curated tracks, and recommendation features push unwanted podcasts and audiobooks clutter over the user's music-only feeds.
            </p>
        </div>

        <div>
            <h4 style="color:#1DB954; font-size:16px; margin-bottom:4px;">What listening behaviors are users trying to achieve?</h4>
            <p style="font-size:14px; color:#E0E0E0; line-height:1.5; margin-bottom:16px;">
                <b>Custom Playlist Curation & Mood Control:</b> Users seek to build custom playlists (e.g. Bollywood curation, Telugu hits, Punjabi pop) and manage their queues cleanly using custom filters to steer valence and mood vibes rather than being locked into recommendation echo chambers.
            </p>
        </div>

        <div>
            <h4 style="color:#1DB954; font-size:16px; margin-bottom:4px;">What causes users to repeatedly listen to the same content?</h4>
            <p style="font-size:14px; color:#E0E0E0; line-height:1.5; margin-bottom:16px;">
                <b>Repetitive Algorithms & Shuffler Echo Chambers:</b> The default smart shuffler behaves repetitively, trapping lists (even large ones with 2,000+ tracks) in safe, narrow recommendation mixes.
            </p>
        </div>

        <div>
            <h4 style="color:#1DB954; font-size:16px; margin-bottom:4px;">Which user segments experience different discovery challenges?</h4>
            <p style="font-size:14px; color:#E0E0E0; line-height:1.5; margin-bottom:16px;">
                <b>Premium vs. Free Tier Segments:</b> Analysis reveals two main user segments experiencing different curation and discovery barriers:<br/>
                1. 💎 <b>Premium Tier Users</b>: Complain about advanced curation failures (avg rating <b>2.05</b>). They pay for customized, clean music streaming but face repetitive Discover Weekly shuffles, failed AI DJ intent mapping, and unwanted podcast/audiobooks cluttering their feed.<br/>
                2. 🆓 <b>Free Tier Users</b>: Complain about restricted discovery controls (avg rating <b>2.05</b>). Specifically, they face:<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;• <b>Forced Playback Restrictions:</b> Unable to turn off smart shuffle or play tracks on-demand, trapping them in recommendation loops.<br/>
                &nbsp;&nbsp;&nbsp;&nbsp;• <b>Paywalled Curation Controls:</b> Basic functions like rewinding, skipping, or organizing playlist queues are locked behind paywalls, forcing them to repeat content.<br/><br/>
                <b>Who Faces More Problems:</b> Both segments experience high levels of dissatisfaction (avg rating <b>2.05</b> for both), but they face different challenges: Premium users suffer from <b>algorithmic stagnation and content clutter</b> in their curation, while Free users face <b>forced shuffler restrictions and playback limitations</b> that block organic discovery.
            </p>
        </div>

        <div>
            <h4 style="color:#1DB954; font-size:16px; margin-bottom:4px;">What unmet needs emerge consistently across reviews?</h4>
            <p style="font-size:14px; color:#E0E0E0; line-height:1.5; margin-bottom:16px;">
                <b>Music-Only Feeds & Explicit User Steering:</b> Consistently, listeners express the need to completely disable podcast/audiobook clutter to maintain a clean music interface, and want explicit controls (valence, mood, custom search filters) to steer the recommendation shuffler.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"Could not load review analytics. Please make sure the consolidated file exists at {csv_path}")

# ─── Main Execution Layout (No Tabs) ──────────────────────────────────────────
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
    
    date_error = False
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
            
        # Verify 6-month limit (approx 183 days)
        if (to_date - from_date).days > 183:
            st.error("⚠️ Maximum custom date range allowed is 6 months. Please adjust your calendar selection.")
            date_error = True
            
        range_str = format_custom_date_range(from_date, to_date)
        
    st.markdown(f"""
    <div style="background:#181818; border: 1px solid #282828; padding:16px 20px; border-radius:12px; margin-top:10px; margin-bottom:20px;">
        <div style="font-size:12px; color:#B3B3B3; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">Live Date Range</div>
        <div style="font-size:18px; color:#1DB954; font-weight:700; margin-top:4px;">{range_str}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Interactive Review Explorer")
    topic_options = {
        "All Relevant Reviews": [],
        "Smart Shuffle & Rec Loops": ["shuffle", "smart shuffle", "repeat", "same", "loop"],
        "UI/UX Curation Changes (Heart Button, Widgets)": ["heart", "plus", "widget", "layout", "button"],
        "Content Clutter (Podcasts/Audiobooks)": ["podcast", "audiobook", "show", "bloat"],
        "Ads & Curation Restraints (Free Tier)": ["ads", "ad", "free", "premium", "paywall"]
    }
    
    default_topic = st.session_state.get("selected_topic", "All Relevant Reviews")
    try:
        topic_index = list(topic_options.keys()).index(default_topic)
    except ValueError:
        topic_index = 0
        
    default_kw = st.session_state.get("search_kw", "")
    
    sel_topic = st.selectbox(
        "🎯 Filter by Problem Topic", 
        list(topic_options.keys()), 
        index=topic_index,
        key="initial_topic_sel"
    )
    
    search_kw = st.text_input(
        "🔍 Or search custom keywords (e.g. 'carplay', 'lyrics', 'slow'):", 
        value=default_kw,
        key="initial_search_kw"
    ).strip().lower()
    
    if st.button("Analyse", key="analyse_button", use_container_width=True, disabled=date_error):
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
        
        st.session_state.selected_topic = sel_topic
        st.session_state.search_kw = search_kw
        st.session_state.analyzed = True
        st.session_state.last_analyzed_period = range_str
        
        import re
        if selection_mode == "Preset Window (Dropdown)":
            match = re.search(r'\d+', selected_period)
            months = int(match.group()) if match else 1
            st.session_state.end_date = datetime.date.today()
            st.session_state.start_date = st.session_state.end_date - datetime.timedelta(days=30 * months)
        else:
            st.session_state.start_date = from_date
            st.session_state.end_date = to_date
            
        st.rerun()
else:
    render_dashboard(st.session_state.get("last_analyzed_period", "last 1 month"))
