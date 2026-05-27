from dash import Input, Output, no_update, html
from dashboard.app import app
from src.collect_tweet import fetch_tweets, _credentials_set
from src.preprocess import clean_tweet
from src.predict_sentiment import predict_sentiment
from src.utils import RollingWindow
import plotly.graph_objs as go
from datetime import datetime, timezone

# Rolling window to store last 50 sentiment scores
window = RollingWindow(maxlen=50)

@app.callback(
    Output('sentiment-graph', 'figure'),
    Output('status-message', 'children'),
    Output('tweets-container', 'children'),
    Input('interval-component', 'n_intervals'),
    Input('keyword-input', 'value')
)
def update_dashboard(n_intervals, keyword):
    if not keyword or keyword.strip() == "":
        # No keyword entered – show empty graph and empty message
        fig = go.Figure()
        fig.update_layout(
            title="Enter a keyword above to start", 
            xaxis_title="Time", 
            yaxis_title="Sentiment Score",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        empty_msg = html.Div(
            "Enter a keyword or brand name to start analyzing sentiment.", 
            style={'color': '#94a3b8', 'textAlign': 'center', 'marginTop': '30px', 'fontSize': '14px'}
        )
        return fig, "Waiting for keyword...", empty_msg
    
    # Fetch tweets
    tweets = fetch_tweets(keyword.strip())
    if not tweets:
        no_tweets_msg = html.Div(
            f"No tweets found for '{keyword}'.", 
            style={'color': '#94a3b8', 'textAlign': 'center', 'marginTop': '30px', 'fontSize': '14px'}
        )
        return no_update, f"No tweets found for '{keyword}'. Try another keyword.", no_tweets_msg
    
    # Process each tweet
    scores = []
    tweet_cards = []
    
    for tweet in tweets:
        cleaned = clean_tweet(tweet['text'])
        score = predict_sentiment(cleaned)
        scores.append(score)
        
        # Sentiment scale categories (No emojis)
        if score >= 0.5:
            label = "Very Positive"
            bg_color = "#dcfce7"
            text_color = "#15803d"
        elif score >= 0.05:
            label = "Positive"
            bg_color = "#ecfdf5"
            text_color = "#047857"
        elif score > -0.05:
            label = "Neutral"
            bg_color = "#f1f5f9"
            text_color = "#475569"
        elif score > -0.5:
            label = "Negative"
            bg_color = "#fee2e2"
            text_color = "#b91c1c"
        else:
            label = "Very Negative"
            bg_color = "#fff1f2"
            text_color = "#be123c"
            
        card = html.Div([
            # Sentiment Badge and Score
            html.Div([
                html.Span(label, style={
                    'backgroundColor': bg_color,
                    'color': text_color,
                    'padding': '3px 10px',
                    'borderRadius': '12px',
                    'fontSize': '12px',
                    'fontWeight': '600',
                    'marginRight': '10px'
                }),
                html.Span(f"Score: {score:+.2f}", style={
                    'color': '#64748b',
                    'fontSize': '12px',
                    'fontWeight': '500'
                })
            ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '8px'}),
            
            # Tweet text
            html.P(tweet['text'], style={
                'margin': '0 0 10px 0',
                'fontSize': '14px',
                'color': '#334155',
                'lineHeight': '1.5'
            }),
            
            # Footer: metrics + posted-at timestamp
            html.Div([
                html.Span(f"Likes: {tweet.get('like_count', 0)}", style={'marginRight': '15px'}),
                html.Span(f"Retweets: {tweet.get('retweet_count', 0)}", style={'marginRight': '15px'}),
                html.Span(
                    _fmt_created_at(tweet.get('created_at')),
                    style={'marginLeft': 'auto', 'fontStyle': 'italic'}
                ),
            ], style={
                'fontSize': '11px',
                'color': '#94a3b8',
                'display': 'flex',
                'alignItems': 'center'
            })
        ], style={
            'backgroundColor': '#ffffff',
            'border': '1px solid #f1f5f9',
            'borderRadius': '8px',
            'padding': '16px',
            'marginBottom': '12px',
            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.02)',
            'transition': 'transform 0.15s ease, box-shadow 0.15s ease'
        })
        tweet_cards.append(card)
    
    avg_score = sum(scores) / len(scores) if scores else 0
    current_time = datetime.now()
    window.append(current_time, avg_score)
    
    times, values = window.get_lists()
    
    # Create graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=values,
        mode='lines+markers',
        name='Sentiment',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#1d4ed8', symbol='circle')
    ))
    
    fig.update_layout(
        title=f"Real-Time Sentiment for '{keyword}'",
        title_font=dict(size=16, family="Plus Jakarta Sans, sans-serif", color='#1e293b'),
        xaxis_title="Time",
        yaxis_title="Average Sentiment Score",
        yaxis=dict(range=[-1.05, 1.05], gridcolor='#f1f5f9', zerolinecolor='#cbd5e1'),
        xaxis=dict(gridcolor='#f1f5f9'),
        plot_bgcolor='#ffffff',
        paper_bgcolor='#ffffff',
        margin=dict(l=40, r=20, t=40, b=40),
        font=dict(family="Plus Jakarta Sans, sans-serif", color='#64748b')
    )
    
    source_label = "X (Real-Time)" if _credentials_set() else "Google News RSS"
    status = (
        f"Source: {source_label}  |  "
        f"Last update: {current_time.strftime('%H:%M:%S')}  |  "
        f"Posts analyzed: {len(tweets)}  |  "
        f"Avg sentiment: {avg_score:+.2f}"
    )
    return fig, status, tweet_cards


# ── helpers ──────────────────────────────────────────────────────────────────
def _fmt_created_at(value) -> str:
    """Return a human-readable timestamp string from various formats twikit/RSS may give."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%b %d, %H:%M")
    # twikit returns an ISO string like 'Tue May 26 11:23:45 +0000 2026'
    try:
        dt = datetime.strptime(str(value), "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%b %d, %H:%M")
    except Exception:
        return str(value)[:16]