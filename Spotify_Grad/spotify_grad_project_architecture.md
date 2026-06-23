# Capstone / Grad Project Architecture: AI-Native Solution for Spotify Music Discovery

**Project Title:** Addressing the "Echo Chamber" Effect in Recommendation Systems using AI-Driven Intent Mapping
**Domain:** Product Management, AI Engineering, and UX Research

This document details the single, consolidated, phase-wise architecture and methodology for the Spotify Graduation Project. It serves as the single source of truth for the project's technical specifications and layout designs.

---

## Phase 1: AI-Powered Review Discovery Engine
**Objective:** Systematically ingest, process, and analyze qualitative user feedback to identify recommendation failures, focusing on music discovery and repetitive listening habits.

### 1.1 Ingestion Layer & Dataset Parameters
*   **Total Review Volume Cap:** Capped at exactly **2,000 reviews** per analysis run.
*   **Equal Platform Distribution:** Exactly **400 reviews** are collected per platform group to ensure unbiased comparative analysis:
    1.  **Google Play Store:** Ingested referencing the package URL `https://play.google.com/store/apps/details?id=com.spotify.music&hl=en_IN` (scraped using `google-play-scraper`).
    2.  **Apple App Store:** Ingested referencing the product URL `https://apps.apple.com/us/app/spotify-music-and-podcasts/id324684580` (targeting the India region customer reviews feed).
    3.  **Community Forums:** Ingested tracking the official boards:
        *   `community.spotify.com/t5/Help`
        *   `community.spotify.com/t5/Ongoing-Issues`
        *   `community.spotify.com/t5/Ideas`
    4.  **Reddit Discussions:** Extracted public discussion posts on subreddits (`r/truespotify` and `r/spotify`) containing hashtags `#SpotifyUpdate`, `#SpotifyDJ`, or `#Daylist`.
    5.  **Social Media Conversations:** Curated public comments from Twitter, Instagram, and Facebook containing hashtags `#SpotifyUpdate`, `#SpotifyDJ`, or `#Daylist`.
*   **Indian Contextualization (Localization):** The ingested reviews are localized to feature Indian musical contexts (e.g., Bollywood tracks, Hindi daily mixes, Tamil melodies, Punjabi pop, Telugu hits, Malayalam soft melodies).
*   **Bypassed Assets:** The legacy `250_spotify_reviews.md` document is entirely bypassed to favor clean, direct ingestion feeds.

### 1.2 Processing & Relevance Filtering
*   **Cleaning:** Standard NLP sanitization removing PII and boilerplate text.
*   **Relevance Filtering:** Keyword matching checks for discovery keywords (e.g. *shuffle*, *recommend*, *loop*, *weekly*, *mix*) against noise keywords (e.g. *payment*, *billing*, *crash*, *lagging*). Only reviews focusing strictly on recommendation behavior are kept.
*   **Vectorization & Storage:** Filtered reviews are converted into dense vector embeddings and indexed in a Vector Database (ChromaDB) to enable RAG-based thematic querying.

### 1.3 LLM-Driven Analysis (The "Agent")
*   **Model:** `llama-3.3-70b-versatile` via Groq.
*   **Token Allocation (128k Context Window):** 118,000 tokens are reserved for review data, enabling the direct processing of up to ~1,300 mixed reviews in a single context window.
*   **Thematic Synthesis:** RAG queries cluster insights to compile answers for the six core UX discovery research questions:
    1.  Why do users struggle to discover new music?
    2.  What are the most common frustrations with recommendations?
    3.  What listening behaviors are users trying to achieve?
    4.  What causes users to repeatedly listen to the same content?
    5.  Which user segments experience different discovery challenges?
    6.  What unmet needs emerge consistently across reviews?

---

## Phase 2: Validate the Opportunity Through User Research
**Objective:** Ground LLM-generated hypotheses in primary, qualitative user research.

### 2.1 Methodology & Guide Creation
*   **AI-Assisted Guide Creation:** Use insights from Phase 1 to automatically generate semi-structured interview scripts using the LLM.
*   **Screener:** Target 5-6 participants matching the "High-Engagement, Low-Discovery" user profile.

### 2.2 Transcription & Synthesis
*   **Whisper Transcription:** Audio from interviews is transcribed using **OpenAI Whisper**.
*   **LLM Synthesis:** Feed transcriptions into the LLM context window to extract patterns and validate the core target persona: the **"Active Curation Seeker"**.

---

## Phase 3: Define the Problem
**Objective:** Frame a clear, business-driven problem statement in a Product Requirements Document (PRD).

*   **Root Cause Hypothesis:** *Traditional collaborative filtering models over-optimize for engagement (watch/listen time), trapping users in local minima. Users lack semantic controls to steer the algorithm out of its echo chambers.*
*   **Business Case:** Boosting music discovery diversity directly increases long-term retention (LTV) and reduces churn to competitor platforms.

---

## Phase 4: Build an AI-Native MVP ("Spotify Vibe Steer")
**Objective:** Deploy a functional MVP prototype demonstrating how conversational AI can translate natural human intent into Spotify Web API parameters.

### 4.1 Frontend Interface (Streamlit Dashboard Layout & Specifications)
*   **Single-Page Layout:** Toggled via `st.session_state.analyzed` to prevent duplicate key errors.
*   **Graphs on Top:** Displays metric summaries and platform feedback/rating distribution tables at the very top of the page.
*   **1-Based Table Indexing:** The indexes of the feedback and rating distribution tables start at **1** instead of **0**.
*   **Stacked Pre-Filters:** The **Interactive Review Explorer** topic filter dropdown is integrated in the initial Time Period configuration screen.
*   **Shuffled Review Display:** Reviews in the explorer are randomized to show a mixture of all platform categories, numbered sequentially starting at `#1`, with formatted dates using capitalized months (e.g. `22 June 2026`).
*   **Custom Explorer Caption:** Displays the simplified reviews caption: `"listing top 20 reviews from various platform."`
*   **6-Month Calendar picker limits:** The Custom Calendar date picker restricts selections to a **maximum of 6 months**. Validations automatically display an error block and disable the **Analyse** button if the limit is exceeded.
*   **Q&A Insights at Bottom (Quote-Free Synthesis):** The 6 core Product Discovery Q&A panels are positioned at the very bottom of the dashboard, displaying majority-based synthesized trends with no individual review quote blocks. Under the user segments panel, it displays the Premium vs. Free tier segments with average rating metrics, outlining their unique discovery barriers and playback problems.

### 4.2 Backend Integration (FastAPI Layer)
*   Exposes endpoints to orchestrate recommendations and route prompt intents.
*   Uses **Spotify Web API** for OAuth, fetching user top track profiles, and querying `/recommendations` parameters.

### 4.3 AI Engine (The Intent Router)
*   Translates natural language prompts into seed genres, target valence, energy, and acousticness values.
*   Returns retrieved tracks along with Explainable AI (XAI) justifications.
