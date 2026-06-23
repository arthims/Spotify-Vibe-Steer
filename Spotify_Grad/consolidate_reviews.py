import os
import re
import pandas as pd

# Define paths
csv_path = r"C:\Users\SDS01493\.gemini\antigravity\scratch\Spotify_Grad\spotify_google_play_reviews.csv"
md_path = r"C:\Users\SDS01493\.gemini\antigravity\brain\32ac3bfd-2c41-4a3e-893c-9749c777098b\250_spotify_reviews.md"

# Output paths
outputs = [
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Spotify_Grad\Reviews_Spotify.csv",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Spotify_Grad\Reviews_Spotify.xlsx",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify.csv",
    r"C:\Users\SDS01493\.gemini\antigravity\scratch\Reviews_Spotify.xlsx"
]

def parse_md_reviews(filepath):
    print(f"Parsing markdown reviews from: {filepath}")
    reviews = []
    current_platform = None
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str.startswith("## "):
                header = line_str[3:].strip()
                if "Google Play" in header:
                    current_platform = "Google Play"
                elif "Apple App Store" in header or "App Store" in header:
                    current_platform = "App Store"
                elif "Reddit" in header:
                    current_platform = "Reddit"
                elif "Community Forums" in header or "Community Forum" in header:
                    current_platform = "Community Forums"
                elif "Social Media" in header:
                    current_platform = "Social Media"
                continue
            
            # Match list item, e.g., "1. " or "100. "
            m = re.match(r'^(\d+)\.\s*(.*)', line_str)
            if m and current_platform:
                rest = m.group(2).strip()
                
                # Check for rating, e.g., "- *5 Stars*"
                rating = None
                rating_match = re.search(r'-\s*\*(\d+)\s+Stars?\*', rest)
                if rating_match:
                    rating = int(rating_match.group(1))
                    rest = rest[:rating_match.start()].strip()
                
                # Extract quoted review text
                quote_match = re.match(r'^"(.*)"$', rest)
                if quote_match:
                    review_text = quote_match.group(1)
                else:
                    if rest.startswith('"') and rest.endswith('"'):
                        review_text = rest[1:-1]
                    else:
                        review_text = rest
                
                review_text = review_text.replace('\\"', '"').strip()
                
                reviews.append({
                    "Review_ID": None,
                    "User_Name": None,
                    "Platform": current_platform,
                    "Rating": rating,
                    "Thumbs_Up_Count": None,
                    "Review_Text": review_text,
                    "Date": None
                })
    
    print(f"Successfully parsed {len(reviews)} reviews from markdown.")
    return reviews

def consolidate():
    # 1. Parse CSV
    print(f"Reading CSV reviews from: {csv_path}")
    if os.path.exists(csv_path):
        df_csv = pd.read_csv(csv_path)
        # Rename columns to match unified schema
        df_csv = df_csv.rename(columns={
            "Review ID": "Review_ID",
            "User Name": "User_Name",
            "Score": "Rating",
            "Thumbs Up Count": "Thumbs_Up_Count",
            "Review Text": "Review_Text",
            "Date": "Date"
        })
        df_csv["Platform"] = "Google Play"
        print(f"Successfully read {len(df_csv)} reviews from CSV.")
    else:
        print(f"Warning: CSV file not found at {csv_path}")
        df_csv = pd.DataFrame(columns=["Review_ID", "User_Name", "Platform", "Rating", "Thumbs_Up_Count", "Review_Text", "Date"])

    # 2. Parse Markdown
    md_reviews = []
    if os.path.exists(md_path):
        md_reviews = parse_md_reviews(md_path)
    else:
        print(f"Warning: Markdown file not found at {md_path}")
        
    df_md = pd.DataFrame(md_reviews)
    
    # 3. Combine both
    df_combined = pd.concat([df_csv, df_md], ignore_index=True)
    
    # Reorder columns to be logical and tidy
    columns_order = ["Review_ID", "User_Name", "Platform", "Rating", "Thumbs_Up_Count", "Review_Text", "Date"]
    df_combined = df_combined[columns_order]
    
    # De-duplicate by Review_Text within the same Platform to avoid duplicates
    before_len = len(df_combined)
    df_combined = df_combined.drop_duplicates(subset=["Platform", "Review_Text"])
    after_len = len(df_combined)
    print(f"De-duplicated: removed {before_len - after_len} duplicate reviews. Total remaining: {after_len}.")
    
    # 4. Save to target files
    for output_path in outputs:
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        if output_path.endswith(".csv"):
            print(f"Saving to CSV: {output_path}")
            df_combined.to_csv(output_path, index=False, encoding="utf-8-sig")
        elif output_path.endswith(".xlsx"):
            print(f"Saving to Excel: {output_path}")
            try:
                df_combined.to_excel(output_path, index=False)
            except Exception as e:
                print(f"Could not save to Excel due to error: {e}. Attempting to install openpyxl...")
                # We will handle it outside or just log it
                raise e
                
    # Print statistics
    print("\nSummary of consolidated reviews by platform:")
    print(df_combined["Platform"].value_counts())

if __name__ == "__main__":
    consolidate()
