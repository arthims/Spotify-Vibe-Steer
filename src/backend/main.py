import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from groq import Groq
from dotenv import load_dotenv
import math

load_dotenv()

app = FastAPI(title="Spotify Vibe Steer API")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# Load Mock Music Catalog from generated JSON
try:
    with open("src/backend/catalog.json", "r") as f:
        MOCK_CATALOG = json.load(f)
except FileNotFoundError:
    MOCK_CATALOG = []

class ChatRequest(BaseModel):
    user_prompt: str
    language: Optional[str] = None
    genre: Optional[str] = None
    era: Optional[str] = None

class Track(BaseModel):
    id: str
    name: str
    artist: str
    genre: str
    language: str
    era: str

class ChatResponse(BaseModel):
    tracks: list[Track]
    explanation: str

def get_recommendations(target_valence: float, target_energy: float, target_lang: str, target_genre: str, target_era: str):
    scored_tracks = []
    for track in MOCK_CATALOG:
        # Strict filtering to ensure accuracy
        if target_lang and track["language"].lower() != target_lang.lower():
            continue
        if target_genre and track["genre"].lower() != target_genre.lower():
            continue
        if target_era and track["era"].lower() != target_era.lower():
            continue

        # If it passes the strict filters, calculate distance based on mood
        dist = math.sqrt((track["valence"] - target_valence)**2 + (track["energy"] - target_energy)**2)
        scored_tracks.append({"track": track, "score": dist})
    
    # Sort by closest vibe match
    scored_tracks.sort(key=lambda x: x["score"])
    top_tracks = [item["track"] for item in scored_tracks[:3]]
    
    # Fallback if no exact match is found (relax era first, then genre, then language)
    if not top_tracks:
        for track in MOCK_CATALOG:
            penalty = 0.0
            if target_lang and track["language"].lower() != target_lang.lower(): penalty += 100
            if target_genre and track["genre"].lower() != target_genre.lower(): penalty += 50
            if target_era and track["era"].lower() != target_era.lower(): penalty += 10
            
            dist = math.sqrt((track["valence"] - target_valence)**2 + (track["energy"] - target_energy)**2) + penalty
            scored_tracks.append({"track": track, "score": dist})
        scored_tracks.sort(key=lambda x: x["score"])
        top_tracks = [item["track"] for item in scored_tracks[:3]]

    return top_tracks

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    system_prompt = f"""
    You are the Spotify Vibe Steer Agent. The user will give you a natural language request.
    Extract the intent to audio features:
    - target_valence (0.0 to 1.0)
    - target_energy (0.0 to 1.0)
    
    UI Defaults provided: Language={req.language}, Genre={req.genre}, Era={req.era}.
    
    Output strictly JSON matching this schema:
    {{
        "target_valence": float,
        "target_energy": float,
        "target_genre": string or null,
        "target_language": string or null,
        "target_era": string or null
    }}
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.user_prompt}
            ],
            model=MODEL,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        intent_json = json.loads(response.choices[0].message.content)
        t_val = intent_json.get("target_valence", 0.5)
        t_nrg = intent_json.get("target_energy", 0.5)
        
        # UI explicit selections strictly override LLM extraction to guarantee correctness
        t_gen = req.genre if req.genre else intent_json.get("target_genre")
        t_lang = req.language if req.language else intent_json.get("target_language")
        t_era = req.era if req.era else intent_json.get("target_era")

        recommended = get_recommendations(t_val, t_nrg, t_lang, t_gen, t_era)

        track_names = ", ".join([f"{t['name']} by {t['artist']}" for t in recommended])
        explain_prompt = f"""
        User requested: "{req.user_prompt}" 
        Filters Applied: Lang={t_lang}, Genre={t_gen}, Era={t_era}.
        You extracted: Valence={t_val}, Energy={t_nrg}.
        The system retrieved these tracks: {track_names}.
        
        In 2-3 short conversational sentences, explain to the user WHY these specific tracks were chosen for them, mentioning the language, genre, and era match.
        """
        
        exp_response = client.chat.completions.create(
            messages=[{"role": "system", "content": "You are a helpful AI music curator."},
                      {"role": "user", "content": explain_prompt}],
            model=MODEL,
            temperature=0.7
        )
        explanation = exp_response.choices[0].message.content

        tracks_out = [Track(**t) for t in recommended]
        return ChatResponse(tracks=tracks_out, explanation=explanation)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
