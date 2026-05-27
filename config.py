import os
from dotenv import load_dotenv
load_dotenv()
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("TWITTER_BEARER_ACCOUNT")
if not TWITTER_BEARER_TOKEN:
    raise ValueError("Twitter Bearer Token is not set. Please set TWITTER_BEARER_TOKEN or TWITTER_BEARER_ACCOUNT in the .env file.")

# X account credentials for twikit (real-time scraping, no paid API needed)
X_USERNAME = os.getenv("X_USERNAME", "")
X_EMAIL    = os.getenv("X_EMAIL", "")
X_PASSWORD = os.getenv("X_PASSWORD", "")

MAX_TWEETS = 100 ##how many tweet it will fetchh
TWEET_LANG = 'en'
MODEL_PATH = "models/bert_tiny_sentiment" #using berttiny sentimentanalysis
UPDATE_INTERVAL_SECONDS = 30     ##how often will the new tweets be fetched and graph updated (30s needed for 100 tweets)
DASHBOARD_PORT = 8050
DASHBOARD_HOST = "0.0.0.0"  
DEBUG_MODE = False  #i will make it false in production

EXCLUDE_RETWEETS = True 
