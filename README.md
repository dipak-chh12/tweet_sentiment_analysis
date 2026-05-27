a tool that parses real time twitter data about a particular keyword and performs sentiment analysis

```text
├── config.py                 # Central configurations (ports, limits, models)
├── run.py                    # App entrypoint
├── setup_cookies.py          # Auto login and cookie generator (legacy)
├── setup_cookies_manual.py   # Cookie builder (recommended bypass method)
├── requirements.txt          # Python dependencies
├── dashboard/
│   ├── app.py                # Dash core layout & styling
│   └── callbacks.py          # State updates, graph logic & UI cards
└── src/
    ├── collect_tweet.py      # Multi-tier ingestion engine
    ├── predict_sentiment.py  # Model inference and scoring
    └── preprocess.py         # Tweet cleaning / text normalizer
