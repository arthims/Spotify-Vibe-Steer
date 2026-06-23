import pandas as pd
from google_play_scraper import Sort, reviews, reviews_all
import praw
import time
import datetime

# ==========================================
# 1. GOOGLE PLAY STORE SCRAPER
# ==========================================
def scrape_google_play(target_count=2000):
    print(f"[*] Starting Google Play scraper... Target: {target_count} reviews")
    
    # We use the standard reviews function with continuation tokens to fetch batches
    collected_reviews = []
    continuation_token = None
    
    # Fetch in batches of 200 (the max allowed per request usually)
    while len(collected_reviews) < target_count:
        try:
            result, continuation_token = reviews(
                'com.spotify.music',
                lang='en', 
                country='us',
                sort=Sort.NEWEST,
                count=200,
                continuation_token=continuation_token
            )
            
            for r in result:
                collected_reviews.append({
                    "Platform": "Google Play",
                    "Date": r['at'],
                    "Rating": r['score'],
                    "Review_Content": r['content'].replace('\n', ' ')
                })
                
            print(f"    -> Fetched {len(collected_reviews)} Google Play reviews so far...")
            
            # If there's no token, we've hit the end of available reviews
            if not continuation_token:
                break
                
            time.sleep(1) # Be polite to the server
            
        except Exception as e:
            print(f"[!] Error fetching Play Store reviews: {e}")
            break
            
    # Trim exactly to target count
    return collected_reviews[:target_count]

# ==========================================
# 2. REDDIT API SCRAPER
# ==========================================
def scrape_reddit(client_id, client_secret, user_agent, target_count=2000):
    print(f"\n[*] Starting Reddit scraper... Target: {target_count} posts")
    
    try:
        # Authenticate with Reddit
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        collected_posts = []
        
        # Search the truespotify and spotify subreddits
        # Limit is technically 1000 per search query for Reddit API, so we search multiple terms
        search_terms = ['review', 'complaint', 'update', 'feature', 'bug', 'premium']
        
        for term in search_terms:
            if len(collected_posts) >= target_count:
                break
                
            print(f"    -> Searching Reddit for keyword: '{term}'...")
            subreddit = reddit.subreddit('truespotify+spotify')
            
            for submission in subreddit.search(term, sort='new', limit=500):
                if len(collected_posts) >= target_count:
                    break
                    
                # Avoid completely empty posts
                content = submission.selftext.replace('\n', ' ')
                if not content:
                    content = submission.title
                    
                collected_posts.append({
                    "Platform": "Reddit",
                    "Date": datetime.datetime.fromtimestamp(submission.created_utc),
                    "Rating": "N/A", # Reddit doesn't have 1-5 stars
                    "Review_Content": f"[{submission.title}] {content}"
                })
                
        return collected_posts[:target_count]
        
    except Exception as e:
        print(f"[!] Error connecting to Reddit API: {e}")
        print("    Did you enter your Client ID and Client Secret correctly?")
        return []

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == '__main__':
    # ---------------------------------------------------------
    # TODO: PUT YOUR REDDIT API CREDENTIALS HERE
    # ---------------------------------------------------------
    REDDIT_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    REDDIT_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"
    REDDIT_USER_AGENT = "SpotifyReviewScraper_GradProject (by u/your_username)"
    
    TARGET_PER_PLATFORM = 2000
    all_data = []
    
    # 1. Run Play Store Scraper
    play_store_data = scrape_google_play(target_count=TARGET_PER_PLATFORM)
    all_data.extend(play_store_data)
    
    # 2. Run Reddit Scraper (Only runs if you put in your keys)
    if REDDIT_CLIENT_ID != "YOUR_CLIENT_ID_HERE":
        reddit_data = scrape_reddit(
            client_id=REDDIT_CLIENT_ID, 
            client_secret=REDDIT_CLIENT_SECRET, 
            user_agent=REDDIT_USER_AGENT,
            target_count=TARGET_PER_PLATFORM
        )
        all_data.extend(reddit_data)
    else:
        print("\n[!] Skipping Reddit scrape because API keys are missing.")
        
    # 3. Export to CSV and Excel
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Save as CSV
        csv_filename = 'spotify_massive_reviews.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        print(f"\n[+] SUCCESS! Saved {len(df)} total reviews to '{csv_filename}'.")
    else:
        print("\n[-] No data collected.")
