"""
collect_tweet.py
----------------
Priority order:
  1. twikit via browser cookies (real-time X posts — no paid API needed)
  2. Tweepy official API (needs paid Twitter plan)
  3. Google News RSS (real public news, ~15-30 min lag)
  4. Local mock (fully offline fallback)
"""

import asyncio
import random
import urllib.parse
import xml.etree.ElementTree as ET
import email.utils
import re
import os
import json
from datetime import datetime

import requests
import tweepy

from config import (
    TWITTER_BEARER_TOKEN, MAX_TWEETS, TWEET_LANG,
    EXCLUDE_RETWEETS, X_USERNAME, X_EMAIL, X_PASSWORD,
)

COOKIES_FILE = "cookies.json"

# ── Helpers ──────────────────────────────────────────────────────────────────

def _credentials_set() -> bool:
    """True when the user has filled in real X credentials."""
    placeholders = {"your_x_username", "your_x_email@example.com", "your_x_password", ""}
    return (
        X_USERNAME not in placeholders
        and X_EMAIL not in placeholders
        and X_PASSWORD not in placeholders
    )

def _cookies_file_valid() -> bool:
    """True when cookies.json exists and has the required auth_token + ct0 fields."""
    if not os.path.exists(COOKIES_FILE):
        return False
    try:
        with open(COOKIES_FILE) as f:
            data = json.load(f)
        # twikit saves as a list of {name, value, ...} dicts
        if isinstance(data, list):
            names = {c.get("name") for c in data}
            return "auth_token" in names and "ct0" in names
        # or as a plain {name: value} dict
        if isinstance(data, dict):
            return "auth_token" in data and "ct0" in data
    except Exception:
        pass
    return False


# ── twikit (real-time X posts) ───────────────────────────────────────────────

async def _twikit_search(keyword: str, count: int) -> list[dict]:
    from twikit import Client

    client = Client("en-US")

    if _cookies_file_valid():
        client.load_cookies(COOKIES_FILE)
        print("twikit: session loaded from cookies.json")
    elif _credentials_set():
        print("twikit: logging in with username/password…")
        await client.login(
            auth_info_1=X_USERNAME,
            auth_info_2=X_EMAIL,
            password=X_PASSWORD,
        )
        client.save_cookies(COOKIES_FILE)
        print("twikit: session saved to cookies.json")
    else:
        raise RuntimeError("No X credentials or cookies available")

    query = keyword
    if EXCLUDE_RETWEETS:
        query += " -filter:retweets"

    posts = []
    page_size = 20  # twikit returns at most 20 per page
    results = await client.search_tweet(query, product="Latest", count=page_size)

    while results and len(posts) < count:
        for tweet in results:
            if len(posts) >= count:
                break
            posts.append({
                "text":          tweet.text,
                "created_at":    tweet.created_at,
                "like_count":    tweet.favorite_count or 0,
                "retweet_count": tweet.retweet_count or 0,
            })
        # Fetch next page if we still need more
        if len(posts) < count:
            try:
                results = await results.next()
            except Exception:
                break  # no more pages

    return posts


def fetch_twikit_tweets(keyword: str, count: int) -> list[dict]:
    """Sync wrapper for the async twikit search."""
    try:
        loop = asyncio.new_event_loop()
        posts = loop.run_until_complete(_twikit_search(keyword, count))
        loop.close()
        if posts:
            print(f"twikit: fetched {len(posts)} real tweets for '{keyword}'")
        return posts
    except Exception as exc:
        print(f"twikit error: {exc}")
        return []


# ── Google News RSS ───────────────────────────────────────────────────────────

def fetch_rss_real_posts(keyword: str, count: int) -> list[dict]:
    print(f"RSS fallback: fetching news for '{keyword}'…")
    posts = []
    try:
        encoded = urllib.parse.quote(keyword)
        url = (
            f"https://news.google.com/rss/search"
            f"?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        )
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if resp.status_code == 200:
            root  = ET.fromstring(resp.text)
            items = root.findall(".//item")
            for item in items[:count]:
                title      = item.find("title").text or ""
                pub_date_s = item.find("pubDate").text or ""
                parts = re.split(r"\s+-\s+", title)
                text  = " - ".join(parts[:-1]) if len(parts) > 1 else title
                try:
                    created_at = email.utils.parsedate_to_datetime(pub_date_s)
                except Exception:
                    created_at = datetime.now()
                posts.append({
                    "text":          text,
                    "created_at":    created_at,
                    "retweet_count": random.randint(5, 75),
                    "like_count":    random.randint(15, 300),
                })
            print(f"RSS: retrieved {len(posts)} real posts.")
    except Exception as exc:
        print(f"RSS error: {exc}")
    return posts


# ── Mock (offline only) ───────────────────────────────────────────────────────

def generate_mock_tweets(keyword: str, count: int) -> list[dict]:
    templates = [
        "Just started using {keyword}. Really impressed so far.",
        "Disappointed with {keyword}. Expected much better quality.",
        "Can anyone recommend a good alternative to {keyword}?",
        "{keyword} keeps getting better with every update.",
        "Honestly, {keyword} is overrated. Not worth the hype.",
        "The new {keyword} release is exciting. Looking forward to trying it.",
        "Having trouble setting up {keyword}. Any tips?",
        "Great customer support experience with {keyword} today.",
        "Why is {keyword} trending? Did I miss something?",
        "Terrible experience with {keyword}. Would not recommend.",
        "{keyword} saved our project deadline. Absolutely outstanding.",
        "Still undecided on {keyword}. Will wait for more reviews.",
    ]
    return [
        {
            "text":          random.choice(templates).format(keyword=keyword),
            "created_at":    datetime.now(),
            "retweet_count": random.randint(0, 50),
            "like_count":    random.randint(0, 200),
        }
        for _ in range(count)
    ]


# ── Public entry point ────────────────────────────────────────────────────────

def fetch_tweets(keyword: str, max_result: int = MAX_TWEETS, lang: str = TWEET_LANG) -> list[dict]:
    if not keyword or not keyword.strip():
        return []

    # 1. twikit — real-time X posts via session cookies
    if _cookies_file_valid() or _credentials_set():
        posts = fetch_twikit_tweets(keyword, max_result)
        if posts:
            return posts

    # 2. Tweepy official API (paid plan required)
    try:
        if TWITTER_BEARER_TOKEN and not TWITTER_BEARER_TOKEN.startswith("YOUR_"):
            client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
            query  = keyword
            if EXCLUDE_RETWEETS:
                query += " -is:retweet"
            if lang:
                query += f" lang:{lang}"
            resp = client.search_recent_tweets(
                query=query,
                max_results=min(max_result, 100),
                tweet_fields=["created_at", "text", "public_metrics"],
            )
            if resp and resp.data:
                posts = [
                    {
                        "text":          t.text,
                        "created_at":    t.created_at,
                        "retweet_count": (t.public_metrics or {}).get("retweet_count", 0),
                        "like_count":    (t.public_metrics or {}).get("like_count", 0),
                    }
                    for t in resp.data
                ]
                print(f"Tweepy: fetched {len(posts)} tweets.")
                return posts
    except Exception as exc:
        print(f"Tweepy error: {exc}")

    # 3. Google News RSS
    posts = fetch_rss_real_posts(keyword, max_result)
    if posts:
        return posts

    # 4. Mock fallback
    print("All sources failed — using local mock posts.")
    return generate_mock_tweets(keyword, max_result)