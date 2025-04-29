import aiohttp
import logging
import re
from urllib.parse import quote
from datetime import datetime

async def search_twitter(coin_id: str, symbol: str, token: str):
    """
    Search recent tweets for a given coin using Twitter API v2.
    Args:
        coin_id (str): Coin name (e.g., "sui").
        symbol (str): Coin symbol (e.g., "SUI").
        token (str): Twitter Bearer Token.
    Returns:
        list: List of tweet items with title, url, content, source, date, relevance, tone.
    """
    try:
        # Build query: hashtag OR coin name OR symbol, crypto-related, non-retweet, prefer English
        query = f"#{symbol} OR #{coin_id} OR {coin_id} crypto OR {symbol} crypto -is:retweet lang:en"
        url = f"https://api.twitter.com/2/tweets/search/recent?query={quote(query)}&max_results=25&tweet.fields=author_id,created_at,public_metrics"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    logging.warning(f"Twitter API error: {resp.status} - {await resp.text()}")
                    return []
                data = await resp.json()

                tweets = []
                for tweet in data.get("data", []):
                    text = tweet["text"]
                    
                    # Skip tweets that are too short or don't seem relevant
                    if len(text) < 30 or "RT @" in text:
                        continue
                    
                    # Basic tone analysis for tweet content
                    tone = "Neutral"
                    positive_words = ['bullish', 'surge', 'soar', 'gain', 'rally', 'rise', 'jump', 'growth', 
                                     'record', 'adopt', 'breakthrough', 'opportunity', 'positive', 'strong',
                                     'increase', 'up', 'high', 'moon', 'win', 'profitable', '🚀', '📈', '💰', '💎']
                    
                    negative_words = ['bearish', 'plunge', 'crash', 'fall', 'decline', 'drop', 'tumble', 'slump',
                                      'loss', 'risk', 'warning', 'concern', 'weak', 'volatile', 'dump', 'sell',
                                      'down', 'low', 'bear', 'lose', 'scam', 'fraud', '📉', '⚠️', '❗']
                    
                    pos_count = sum(1 for word in positive_words if word in text.lower())
                    neg_count = sum(1 for word in negative_words if word in text.lower())
                    
                    if pos_count > neg_count:
                        tone = "Positive"
                    elif neg_count > pos_count:
                        tone = "Negative"
                    
                    # Hitung relevansi tweet - improve scoring
                    relevance = (
                        text.lower().count(coin_id.lower()) * 3 +
                        text.lower().count(symbol.lower()) * 3 +
                        text.lower().count(f"#{symbol.lower()}") * 5 +
                        text.lower().count(f"#{coin_id.lower()}") * 5 +
                        (3 if "bullish" in text.lower() or "🚀" in text else 0) +
                        (3 if "bearish" in text.lower() or "📉" in text else 0) +
                        (2 if "price" in text.lower() or "prediction" in text.lower() else 0) +
                        (2 if "analysis" in text.lower() or "chart" in text.lower() else 0) +
                        (3 if "partnership" in text.lower() or "launch" in text.lower() else 0) +
                        (tweet.get("public_metrics", {}).get("like_count", 0) // 5) +  # Likes add to relevance
                        (tweet.get("public_metrics", {}).get("retweet_count", 0) * 2)  # Retweets add more relevance
                    )
                    
                    # Clean up the tweet text by removing URLs and extra spaces
                    clean_text = re.sub(r'http\S+', '', text)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    
                    # Hanya tambahkan ke hasil jika relevansi cukup tinggi
                    if relevance >= 5:
                        tweets.append({
                            "title": clean_text,
                            "url": f"https://x.com/i/status/{tweet['id']}",
                            "content": clean_text,
                            "source": "Twitter",
                            "date": datetime.now().strftime('%Y-%m-%d'),
                            "relevance": relevance,
                            "tone": tone
                        })

                # Sort by relevance
                tweets.sort(key=lambda x: x["relevance"], reverse=True)
                return tweets

    except Exception as e:
        logging.error(f"Error in search_twitter: {str(e)}")
        return []