# Review Analysed: Spotify Music Discovery Q&A Findings

This document contains the detailed qualitative findings from the analysis of the **615 discovery-relevant user reviews** (from a database of 2,412 multi-platform reviews). It serves as a reference for the capstone product requirements and MVP goals.

---

### Q1: Why do users struggle to discover new music?
*   **Recommendation Safety Bias:** The algorithm heavily weights historical data, delivering recommendations that mimic what users already like. This feedback loop excludes new styles and genres, leading to a lack of novelty.
*   **Artist Notification Decoupling:** New releases from followed artists are pushed off the main landing pages, making proactive artist-based discovery difficult.
*   **Sponsored Placement:** Curated radios are perceived as advertising channels promoting paid content rather than organic recommendations.

> *User Quote (Google Play - 2 Stars):* "homepage is full of AI made playlists and recommendations but they are all based on my history and liked songs. I want to Listen something new but there is no way unless I know a few songs myself. no novelty."

---

### Q2: What are the most common frustrations with recommendations?
*   **Forced Smart Shuffle:** Users dislike recommendations being forced onto their carefully curated playlists, overriding standard playback.
*   **Repetitive Shuffle Loop:** Even in massive playlists, the randomizer cycles through the same ~25 songs continuously.
*   **Ad Volume Disruptions:** Intrusive advertisement densities interrupt the listening flow, driving users away.

> *User Quote (Google Play - 1 Star):* "money hungry app forces you to get premium just so you can turn off smart shuffle and play songs that arent in your playlist"

---

### Q3: What listening behaviors are users trying to achieve?
*   **Active steering of recommendation vibes:** Users want to input natural language vibe prompts to steer their selections (e.g. "darker beats", "focus mood").
*   **Pure Music Playback:** Clear division between podcasts/audiobooks and music tracks.
*   **Curation Control:** Simple, immediate queue editing and playlist ordering without paywalls.

> *User Quote (Google Play - 5 Stars):* "Spotify has quite recently added the ability to (un)filter playlists and radios so they aren't customized. I cannot express how important this is to me..."

---

### Q4: What causes users to repeatedly listen to the same content?
*   **Collaborative Filtering Safety:** Standard metrics focus on completion rates, reinforcing loops of safe/familiar plays.
*   **Free-tier paywalls on skip/rewind controls:** Users cannot skip forward or backward, trapping them on default loops.
*   **Broken Randomization:** Algorithms stick to a small memory cache of recently played songs.

> *User Quote (Google Play - 3 Stars):* "please for the love of God fix the shuffle. I swear im experiencing de ja vu multiple times as its always the same selection..."

---

### Q5: Which user segments experience different discovery challenges?
*   **Free-Tier Users:** Restricted from picking songs or playing in order, heavily interrupted by ads.
*   **Premium Power Users:** Annoyed by A/B experiments changing stable UIs, and by podcast injections.
*   **Offline/CarPlay Listeners:** Struggle with bugs that break download lists and CarPlay synchronizations.

> *User Quote (Google Play - 2 Stars):* "Premium is great, but without it you can't do nearly anything except press play and listen to what you've been given"

---

### Q6: What unmet needs emerge consistently across reviews?
*   **Music-Only Tab/Mode:** Option to completely hide podcasts/audiobooks.
*   **Lossless Audio/HiFi Support:** Audiophiles seeking high-bitrate output.
*   **Conversational Customization (AI-driven steering):** Interactive, human-like curation requests.

> *User Quote (Community Forums):* "Idea: Add a 'Music Only' mode to hide podcasts."
