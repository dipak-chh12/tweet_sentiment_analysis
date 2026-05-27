import dash
from dash import dcc, html
from config import UPDATE_INTERVAL_SECONDS

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap'
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Real-Time Brand Sentiment Tracker"

# Premium layout styling
app.layout = html.Div([
    # Header Section
    html.Div([
        html.H1("Real-Time Brand Sentiment Tracker", style={
            'textAlign': 'center', 
            'fontWeight': '700', 
            'color': '#0f172a',
            'marginBottom': '5px'
        }),
        html.P("Analyze and monitor public sentiment dynamically on the web", style={
            'textAlign': 'center',
            'color': '#64748b',
            'fontSize': '16px',
            'marginTop': '0px',
            'marginBottom': '30px'
        })
    ], style={'padding': '20px 0 10px 0'}),
    
    # Search input container
    html.Div([
        html.Div([
            html.Label("Enter Brand or Topic", style={
                'fontWeight': '600', 
                'color': '#334155', 
                'display': 'block',
                'marginBottom': '8px',
                'fontSize': '14px'
            }),
            dcc.Input(
                id='keyword-input',
                type='text',
                placeholder='e.g. Tesla, Apple, SpaceX, AI',
                value='',
                style={
                    'width': '100%',
                    'padding': '12px 16px',
                    'borderRadius': '8px',
                    'border': '1px solid #cbd5e1',
                    'fontSize': '16px',
                    'fontFamily': 'inherit',
                    'boxSizing': 'border-box',
                    'outline': 'none',
                    'boxShadow': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                    'transition': 'all 0.2s ease'
                }
            ),
        ], style={'maxWidth': '500px', 'margin': '0 auto', 'padding': '0 20px'})
    ], style={'marginBottom': '30px'}),
    
    # Grid Content Layout
    html.Div([
        # Left Panel: Graph
        html.Div([
            html.Div([
                html.H3("Sentiment Trend over Time", style={
                    'fontSize': '18px', 
                    'fontWeight': '600', 
                    'color': '#1e293b', 
                    'margin': '0 0 15px 0'
                }),
                dcc.Graph(
                    id='sentiment-graph', 
                    config={'displayModeBar': False},
                    style={'height': '450px'}
                ),
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '25px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.025)',
                'border': '1px solid #f1f5f9'
            })
        ], style={'flex': '1.3', 'minWidth': '350px', 'padding': '0 15px 20px 15px'}),
        
        # Right Panel: Tweets List
        html.Div([
            html.Div([
                html.H3("Recent Tweets & Sentiment Analysis", style={
                    'fontSize': '18px', 
                    'fontWeight': '600', 
                    'color': '#1e293b', 
                    'margin': '0 0 15px 0'
                }),
                html.Div(
                    id='tweets-container',
                    style={
                        'maxHeight': '450px',
                        'overflowY': 'auto',
                        'paddingRight': '5px'
                    }
                )
            ], style={
                'backgroundColor': '#ffffff',
                'padding': '25px',
                'borderRadius': '12px',
                'boxShadow': '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.025)',
                'border': '1px solid #f1f5f9',
                'height': '450px',
                'display': 'flex',
                'flexDirection': 'column'
            })
        ], style={'flex': '1', 'minWidth': '300px', 'padding': '0 15px 20px 15px'} )
        
    ], style={
        'display': 'flex',
        'flexWrap': 'wrap',
        'maxWidth': '1300px',
        'margin': '0 auto',
        'padding': '0 10px'
    }),
    
    # Status bar
    html.Div(
        id='status-message', 
        style={
            'textAlign': 'center', 
            'marginTop': '30px', 
            'color': '#64748b',
            'fontSize': '14px',
            'paddingBottom': '40px'
        }
    ),
    
    dcc.Interval(
        id='interval-component',
        interval=UPDATE_INTERVAL_SECONDS * 1000,  # milliseconds
        n_intervals=0
    ),
], style={
    'backgroundColor': '#f8fafc',
    'minHeight': '100vh',
    'fontFamily': 'Plus Jakarta Sans, system-ui, -apple-system, sans-serif',
    'padding': '10px 0'
})

# Import callbacks to register them
from dashboard import callbacks