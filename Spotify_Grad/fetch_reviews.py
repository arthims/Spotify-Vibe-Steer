import json
from google_play_scraper import Sort, reviews
import requests
import datetime

def fetch_play_store_reviews():
    try:
        result, _ = reviews(
            'com.spotify.music',
            lang='en', country='us',
            sort=Sort.NEWEST, count=50
        )
        return [{"date": str(r['at']), "score": r['score'], "review": r['content']} for r in result]
    except Exception as e:
        return [{"error": str(e)}]

def fetch_app_store_reviews():
    try:
        # iTunes RSS feed provides the 50 most recent reviews
        response = requests.get('https://itunes.apple.com/us/rss/customerreviews/id=324684580/sortBy=mostRecent/json')
        data = response.json()
        entries = data['feed'].get('entry', [])
        # The first entry is usually the app itself, skip if it doesn't have an author
        reviews_list = []
        for e in entries:
            if 'author' in e:
                title = e.get('title', {}).get('label', '')
                content = e.get('content', {}).get('label', '')
                rating = e.get('im:rating', {}).get('label', '')
                reviews_list.append({"score": rating, "review": f"{title} - {content}"})
        return reviews_list[:50]
    except Exception as e:
        return [{"error": str(e)}]

def fetch_reddit_reviews():
    try:
        headers = {'User-agent': 'Mozilla/5.0'}
        response = requests.get('https://www.reddit.com/r/truespotify/search.json?q=review&restrict_sr=1&sort=new&limit=50', headers=headers)
        data = response.json()
        posts = data['data']['children']
        return [{"date": str(datetime.datetime.fromtimestamp(p['data']['created_utc'])), "title": p['data']['title'], "content": p['data'].get('selftext', '')} for p in posts]
    except Exception as e:
        return [{"error": str(e)}]

if __name__ == '__main__':
    data = {
        "play_store": fetch_play_store_reviews(),
        "app_store": fetch_app_store_reviews(),
        "reddit": fetch_reddit_reviews()
    }
    with open('fetched_reviews.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Done")
