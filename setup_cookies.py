"""
setup_cookies.py
----------------
Run this script ONCE to log in to X and save a session cookie file.
After this succeeds, run.py will use those cookies and never need to
log in again (until X expires the session, typically ~30 days).

Usage:
    python setup_cookies.py
"""

import asyncio
import os
import sys

# Make sure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

X_USERNAME = os.getenv("X_USERNAME", "")
X_EMAIL    = os.getenv("X_EMAIL", "")
X_PASSWORD = os.getenv("X_PASSWORD", "")
COOKIES_FILE = "cookies.json"

async def main():
    from twikit import Client

    if not all([X_USERNAME, X_EMAIL, X_PASSWORD]):
        print("ERROR: Fill in X_USERNAME, X_EMAIL, X_PASSWORD in your .env file first.")
        return

    print(f"Logging in as @{X_USERNAME} ...")
    client = Client("en-US")

    try:
        await client.login(
            auth_info_1=X_USERNAME,
            auth_info_2=X_EMAIL,
            password=X_PASSWORD,
        )
        client.save_cookies(COOKIES_FILE)
        print(f"\nSuccess! Session saved to {COOKIES_FILE}")
        print("You can now run:  python run.py")
        
        # Quick sanity check
        print("\nRunning quick search test for 'Python'...")
        results = await client.search_tweet("Python -filter:retweets", product="Latest", count=3)
        print(f"Got {len(results)} live tweets:")
        for i, t in enumerate(results):
            print(f"  {i+1}. {t.text[:90]}...")

    except Exception as e:
        print(f"\nLogin failed: {e}")
        print("\nIf you get 'Couldn't get KEY_BYTE indices', X has temporarily blocked")
        print("automated logins from your IP. Try the cookie method instead:")
        print("\n  1. Open x.com in Chrome/Firefox and log in")
        print("  2. Press F12 > Application > Cookies > https://x.com")
        print("  3. Copy the values of 'auth_token' and 'ct0'")
        print("  4. Add them to .env:")
        print("       X_AUTH_TOKEN = '<your auth_token value>'")
        print("       X_CT0        = '<your ct0 value>'")
        print("  5. Run:  python setup_cookies_manual.py")

if __name__ == "__main__":
    asyncio.run(main())
