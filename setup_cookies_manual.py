"""
setup_cookies_manual.py
-----------------------
Use this if setup_cookies.py fails with 'Couldn't get KEY_BYTE indices'.

Steps:
  1. Open https://x.com in Chrome or Firefox and log in to your account
  2. Press F12 to open DevTools
  3. Go to Application (Chrome) or Storage (Firefox)
  4. Click Cookies > https://x.com
  5. Find the cookie named 'auth_token' and copy its value
  6. Find the cookie named 'ct0' and copy its value
  7. Paste both into your .env file:
       X_AUTH_TOKEN = 'your_auth_token_value_here'
       X_CT0        = 'your_ct0_value_here'
  8. Run this script:  python setup_cookies_manual.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv()

COOKIES_FILE = "cookies.json"

auth_token = os.getenv("X_AUTH_TOKEN", "").strip()
ct0        = os.getenv("X_CT0", "").strip()

if not auth_token or not ct0:
    print("ERROR: Add X_AUTH_TOKEN and X_CT0 to your .env file first.")
    print("\nGet them from your browser:")
    print("  1. Log in to https://x.com")
    print("  2. F12 > Application > Cookies > https://x.com")
    print("  3. Copy the values of 'auth_token' and 'ct0'")
    sys.exit(1)

# twikit's load_cookies expects a plain dictionary of cookie name to value
cookies = {
    "auth_token": auth_token,
    "ct0":        ct0,
}


with open(COOKIES_FILE, "w") as f:
    json.dump(cookies, f, indent=2)

print(f"cookies.json written with auth_token + ct0.")
print("Run:  python run.py")
