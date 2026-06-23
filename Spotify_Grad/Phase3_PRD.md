# Phase 3: Product Requirements Document (PRD) & Problem Definition

**Project:** Spotify AI-Native Discovery (Graduation Project)
**Document Status:** Final (Phase 3 Complete)
**Based on:** Phase 2 User Research Synthesis

---

## 3.1 Problem Framing

### Background
Spotify has successfully acquired millions of users and built one of the world's most sophisticated recommendation systems. However, a significant percentage of listening still comes from repeat playlists, familiar artists, and previously discovered tracks. While this drives raw engagement time, it leads to discovery fatigue.

### The Core Problem Statement
High-engagement Spotify users experience "discovery fatigue" because the current algorithmic features (Discover Weekly, Radio) over-optimize for safety and historical familiarity. Users want to explore new music tailored to highly specific, immediate moods but lack the semantic control to steer the algorithm out of its predictable "echo chamber."

### Target Persona: "The Active Curation Seeker"
* **Demographics / Behaviors:** Listens to music 20+ hours a week. Maintains carefully curated playlists. Highly engaged but increasingly bored with their current library.
* **Pain Points:** 
  * "The algorithm just plays what it thinks I want based on what I played yesterday, not what I actually want right now."
  * Forced to use external workarounds (Reddit, Incognito mode) to trick the algorithm into providing fresh tracks.
* **Unmet Need:** A deterministic, low-friction way to explicitly command the algorithm using natural language intent (e.g., "Give me songs like this, but darker and faster").

### Root Cause Hypothesis
Traditional collaborative filtering and matrix factorization models heavily over-index on historical exploitation (maximizing listen time through proven tracks). They fundamentally lack **contextual intent understanding**. The system operates on *implicit* signals (what you clicked) rather than *explicit* semantics (what you want to feel), trapping the user in local minima.

---

## 3.2 Business Case & Impact

### Why Solve This Now?
As the streaming market saturates, competitive differentiation shifts from catalog size (which is commoditized) to the **quality of discovery**. If power users feel their library is stale, they become highly susceptible to churning to competitors like Apple Music or YouTube Music, or they shift their discovery attention to platforms like TikTok.

### Strategic Alignment
Solving the discovery problem aligns directly with Spotify’s strategic goal to *increase meaningful music discovery and reduce repetitive listening behavior*, ultimately transitioning users from passive listeners to active explorers.

### Expected Metric Impact (KPIs)
To measure the success of an AI-Native solution, we will track the following metrics:

#### 1. Primary Success Metrics
* **Discovery Rate Diversity Index:** The percentage of daily streams originating from artists the user has never listened to before.
* **Session Intent Satisfaction:** Measured via a direct thumbs-up/thumbs-down signal after a user utilizes the new AI discovery feature.

#### 2. Secondary & Guardrail Metrics
* **User Retention (LTV):** Long-term retention of the "Active Curation Seeker" segment.
* **Playlist Save Rate:** The percentage of AI-recommended tracks that are saved to a user's personal playlist.
* **Workaround Reduction:** A decrease in the usage of "Private Session" mode among the target cohort.

---

## Bridge to Phase 4 (Proposed Solution)
To solve this, we cannot simply tweak the existing collaborative filtering weights. We must introduce an **AI-Native Intent Router**. 

By leveraging Large Language Models (LLMs) and Spotify's audio features API (Valence, Energy, Acousticness), we can map a user's natural language request directly to highly specific track attributes, bypassing historical biases and restoring user agency over the discovery experience.
