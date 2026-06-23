import os
import re
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# File paths
csv_path = r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify.csv"
filtered_csv_paths = [
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Spotify_Grad\Reviews_Spotify_Discovery_Filtered.csv",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Spotify_Grad\Reviews_Spotify_Discovery_Filtered.xlsx",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify_Discovery_Filtered.csv",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify_Discovery_Filtered.xlsx"
]

report_paths = [
    r"C:\Users\SDS01493\.gemini\antigravity\brain\32ac3bfd-2c41-4a3e-893c-9749c777098b\thematic_research_report.md",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Spotify_Grad\thematic_research_report.md"
]

# Relevance keywords
discovery_keywords = [
    "discover", "recommend", "recommendation", "algorithm", "shuffle", "smart shuffle", 
    "repeat", "same", "loop", "played", "weekly", "radio", "mix", "daily mix", 
    "vibe", "mood", "echo chamber", "new music", "new songs", "discovery", "curate", "curation", 
    "playlist", "queue", "hear", "listen", "find", "search", "explore", "music only", "podcasts", "audiobooks"
]

irrelevant_keywords = [
    "payment", "billing", "card", "pay", "price", "subscription", "cancel", "refund", 
    "login", "password", "sign in", "crash", "freeze", "slow to load", "crashing", 
    "lagging", "widget", "receipt", "invoice", "banned", "account recovery", "verification"
]

def is_relevant(text):
    if not isinstance(text, str):
        return False
    text_lower = text.lower()
    
    # Check discovery keywords count
    disc_count = sum(1 for kw in discovery_keywords if kw in text_lower)
    # Check noise/irrelevant keywords count
    irr_count = sum(1 for kw in irrelevant_keywords if kw in text_lower)
    
    # We want reviews that focus on recommendations and discovery behavior.
    # 1. If it contains discovery keywords and no noise keywords, it's definitely relevant.
    # 2. If it contains both, it must have a higher density of discovery keywords.
    # 3. If it contains only noise keywords, it's irrelevant.
    if disc_count > 0 and irr_count == 0:
        return True
    elif disc_count > 0 and irr_count > 0:
        return disc_count >= irr_count
    return False

def filter_reviews():
    print(f"Loading consolidated reviews from: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"Error: consolidated file not found at {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} total reviews.")
    
    # Apply filtering
    df["Is_Relevant"] = df["Review_Text"].apply(is_relevant)
    df_filtered = df[df["Is_Relevant"] == True].copy()
    
    # Clean up the Is_Relevant column
    df_filtered = df_filtered.drop(columns=["Is_Relevant"])
    
    print(f"Filtered down to {len(df_filtered)} discovery-relevant reviews (ignored {len(df) - len(df_filtered)} irrelevant reviews).")
    
    # Save outputs
    for path in filtered_csv_paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if path.endswith(".csv"):
            df_filtered.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"Saved filtered CSV to: {path}")
        elif path.endswith(".xlsx"):
            df_filtered.to_excel(path, index=False)
            print(f"Saved filtered Excel to: {path}")
            
    return df_filtered

def generate_thematic_report(df_filtered):
    print("Generating thematic report using Groq...")
    
    # Select a diverse set of representative reviews to send as context (up to 120 reviews to avoid context overload)
    # We'll sample 25 from each platform if available, or fill up to 120 total.
    sampled_reviews = []
    platforms = df_filtered["Platform"].unique()
    
    for platform in platforms:
        df_plat = df_filtered[df_filtered["Platform"] == platform]
        # Sample low and high scores
        sample_size = min(len(df_plat), 24)
        df_sample = df_plat.sample(n=sample_size, random_state=42)
        for _, row in df_sample.iterrows():
            rating_str = f" ({int(row['Rating'])} Stars)" if pd.notna(row['Rating']) else ""
            sampled_reviews.append(f"- [{row['Platform']}{rating_str}]: \"{row['Review_Text']}\"")
            
    reviews_context = "\n".join(sampled_reviews)
    
    # Setup prompt
    system_prompt = "You are a Principal Product Researcher and UX Research Lead. You analyze multi-platform user feedback to generate rigorous, data-driven synthesis reports."
    
    prompt = f"""
    The main goal of our Spotify Graduation Project is to: "Increase meaningful music discovery and reduce repetitive listening behavior."
    
    We have filtered our consolidated user reviews to focus strictly on this problem statement. Below is a representative sample of user feedback across Google Play, App Store, Reddit, Forums, and Social Media:
    
    {reviews_context}
    
    Please write a comprehensive, academic-grade UX Research and Product Analysis Report. Address the following six core questions from our problem statement in detail, using direct references or paraphrased insights from the user feedback:
    
    1. Why do users struggle to discover new music?
    2. What are the most common frustrations with recommendations?
    3. What listening behaviors are users trying to achieve?
    4. What causes users to repeatedly listen to the same content?
    5. Which user segments experience different discovery challenges?
    6. What unmet needs emerge consistently across reviews?
    
    Structure the report with a professional title, executive summary, detailed answers to each question with bullet points, and an 'Actionable Design Recommendations for MVP' section that connects back to our conversational AI intent-routing feature ("Spotify Vibe Steer").
    
    Format the output as clean Markdown.
    """
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not found.")
        return
        
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.3
    )
    
    report_content = response.choices[0].message.content
    
    # Save report
    for r_path in report_paths:
        os.makedirs(os.path.dirname(r_path), exist_ok=True)
        with open(r_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Saved research report to: {r_path}")
        
    print("Report generation complete!")

if __name__ == "__main__":
    df_filtered = filter_reviews()
    if df_filtered is not None:
        generate_thematic_report(df_filtered)
