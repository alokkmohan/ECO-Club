"""
Eco Club Monitoring Dashboard
A read-only Streamlit dashboard for monitoring school notification uploads.
"""

import streamlit as st
import pandas as pd
from data_service import DataService
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import requests
from PIL import Image


# Function to get GitHub repository last update time
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_github_last_update():
    try:
        url = "https://api.github.com/repos/alokkmohan/ECO-Club/commits/main"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            commit_data = response.json()
            commit_date = commit_data['commit']['committer']['date']
            # Convert to readable format
            dt = datetime.strptime(commit_date, '%Y-%m-%dT%H:%M:%SZ')
            return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        pass
    return pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')


# Page configuration
st.set_page_config(
    page_title="UP Secondary Schools Eco Club Monitoring Dashboard",
    page_icon=Image.open("favicon.png"),
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/alokkmohan/ECO-Club',
        'Report a bug': 'mailto:alokmohann@gmail.com',
        'About': '''
        ## UP Secondary Schools Eco Club Dashboard
        
        Monitor notification uploads and tree plantation activities across UP secondary schools.
        
        **Developed by:** Alok Mohan
        '''
    }
)

# Add meta tags for social media sharing
st.markdown("""
    <meta property="og:title" content="UP Secondary Schools Eco Club Dashboard" />
    <meta property="og:description" content="Monitor Eco Club activities, notification uploads, and tree plantation across Uttar Pradesh secondary schools" />
    <meta property="og:type" content="website" />
    <meta name="description" content="Real-time monitoring dashboard for UP Secondary Schools Eco Club activities" />
    <meta name="keywords" content="Eco Club, UP Schools, Tree Plantation, Environmental Monitoring" />
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False, max_entries=1)  # Cache for 1 hour
def load_eco_data():
    """Load and cache data with automatic CSV conversion."""
    data_service = DataService(data_folder=".")
    df, success, error_message = data_service.load_data()
    return df, success, error_message, data_service


def get_visitor_count():
    """Get and update visitor count with active users tracking."""
    counter_file = 'visitor_count.json'
    active_threshold_minutes = 5  # Consider users active if seen in last 5 minutes
    
    # Initialize counter if file doesn't exist
    if not os.path.exists(counter_file):
        counter_data = {
            'total_visits': 0,
            'unique_visitors': set(),
            'active_sessions': {},  # session_id: last_active_timestamp
            'last_updated': None
        }
    else:
        try:
            with open(counter_file, 'r') as f:
                counter_data = json.load(f)
                # Convert list back to set for unique visitors
                counter_data['unique_visitors'] = set(counter_data.get('unique_visitors', []))
                # Get active sessions (default to empty dict if not present)
                counter_data['active_sessions'] = counter_data.get('active_sessions', {})
        except:
            counter_data = {
                'total_visits': 0,
                'unique_visitors': set(),
                'active_sessions': {},
                'last_updated': None
            }
    
    # Get session ID (unique per browser session)
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    
    session_id = st.session_state.session_id
    current_time = datetime.now()
    
    # Increment total visits only once per session
    if 'visit_counted' not in st.session_state:
        counter_data['total_visits'] += 1
        st.session_state.visit_counted = True
    
    # Add unique visitor
    counter_data['unique_visitors'].add(session_id)
    
    # Update active session timestamp
    counter_data['active_sessions'][session_id] = current_time.isoformat()
    
    # Clean up stale sessions (inactive for more than threshold)
    stale_sessions = []
    for sid, last_active in counter_data['active_sessions'].items():
        try:
            last_active_time = datetime.fromisoformat(last_active)
            time_diff = (current_time - last_active_time).total_seconds() / 60  # in minutes
            if time_diff > active_threshold_minutes:
                stale_sessions.append(sid)
        except:
            stale_sessions.append(sid)
    
    # Remove stale sessions
    for sid in stale_sessions:
        del counter_data['active_sessions'][sid]
    
    # Update timestamp
    counter_data['last_updated'] = current_time.isoformat()
    
    # Calculate active users
    active_users = len(counter_data['active_sessions'])
    
    # Save counter (convert set to list for JSON serialization)
    try:
        with open(counter_file, 'w') as f:
            save_data = {
                'total_visits': counter_data['total_visits'],
                'unique_visitors': list(counter_data['unique_visitors']),
                'active_sessions': counter_data['active_sessions'],
                'last_updated': counter_data['last_updated']
            }
            json.dump(save_data, f, indent=2)
    except:
        pass  # Silently fail if can't write
    
    return counter_data['total_visits'], len(counter_data['unique_visitors']), active_users


def main():
    """Main application function."""
    
    # Custom CSS for better styling and mobile responsiveness
    st.markdown("""
        <style>
        /* Main Container Width Control - CENTERED LAYOUT */
        .main .block-container {
            max-width: 1400px !important;
            padding-left: 6rem !important;
            padding-right: 6rem !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        
        /* Header and content centering */
        .stApp > header {
            background-color: transparent;
        }
        
        section[data-testid="stAppViewContainer"] > .main {
            background-color: #f8f9fa;
            padding-left: 3% !important;
            padding-right: 3% !important;
        }
        
        @media (min-width: 1600px) {
            .main .block-container {
                max-width: 1600px !important;
                padding-left: 8rem !important;
                padding-right: 8rem !important;
            }
        }
        
        @media (max-width: 768px) {
            .main .block-container {
                max-width: 100% !important;
                padding-left: 1.5rem !important;
                padding-right: 1.5rem !important;
            }
            
            section[data-testid="stAppViewContainer"] > .main {
                padding-left: 0 !important;
                padding-right: 0 !important;
            }
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 10px 24px;
            background-color: #f0f2f6;
            border-radius: 10px;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50;
            color: white;
        }
        
        /* Card-like container for content */
        .stTabs [data-baseweb="tab-panel"] {
            padding: 24px;
            background-color: #ffffff;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 10px;
        }
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 10px;
            }
            
            .stMetric {
                font-size: 0.9em;
            }
            
            .stDataFrame {
                font-size: 0.8em;
            }
        }
        
        /* Metric cards styling */
        [data-testid="stMetricValue"] {
            font-size: 1.8em;
            font-weight: 600;
        }
        
        /* Button styling */
        .stDownloadButton button {
            border-radius: 10px;
            background-color: #4CAF50;
            color: white;
            font-weight: 600;
            padding: 10px 20px;
        }
        
        .stDownloadButton button:hover {
            background-color: #45a049;
        }
        
        /* Full-width header banner */
        .header-banner {
            background: linear-gradient(135deg, #ff9933 0%, #ff6600 50%, #ff9933 100%);
            padding: 30px 20px;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(255, 102, 0, 0.3);
            text-align: center;
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }
        
        .header-title {
            color: white;
            font-size: 2.5em;
            font-weight: 800;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            letter-spacing: 2px;
        }
        
        .header-subtitle {
            color: white;
            font-size: 1.2em;
            font-weight: 500;
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        }
        
        @media (max-width: 768px) {
            .header-banner::before,
            .header-banner::after {
                font-size: 2em;
                left: 10px;
                right: 10px;
            }
            .header-title {
                font-size: 1.5em;
            }
            .header-subtitle {
                font-size: 0.9em;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color: #1e3a5f;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .filter-label {
            font-weight: 700;
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 10px;
            display: block;
        }
        
        /* Tab Navigation Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #f0f4f8;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background-color: white;
            border-radius: 8px;
            padding: 0 30px;
            font-size: 1.3em;
            font-weight: 700;
            color: #2c3e50;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            border: 2px solid #4a90e2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 2px solid #5568d3 !important;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
        }
        
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 30px;
        }
        
        /* Mobile Responsive Design */
        @media (max-width: 768px) {
            /* Make tabs stack vertically on mobile */
            .stTabs [data-baseweb="tab-list"] {
                flex-direction: column;
                gap: 8px;
                padding: 8px;
            }
            
            .stTabs [data-baseweb="tab"] {
                width: 100%;
                height: 50px;
                padding: 0 20px;
                font-size: 1.1em;
                text-align: center;
            }
            
            /* Make metric cards stack on mobile */
            .metric-card {
                margin-bottom: 15px;
            }
            
            /* Adjust filter container on mobile */
            .filter-container {
                padding: 20px;
            }
            
            /* Reduce header font size on mobile */
            .header-banner h1 {
                font-size: 1.8em !important;
            }
        }
        
        @media (max-width: 480px) {
            /* Extra small devices */
            .stTabs [data-baseweb="tab"] {
                font-size: 1em;
                height: 45px;
                padding: 0 15px;
            }
            
            .header-banner h1 {
                font-size: 1.5em !important;
            }
            
            .filter-container {
                padding: 15px;
            }
            
            .filter-header {
                font-size: 1.2em;
            }
        }
        
        /* Table Styling */
        .dataframe {
            font-size: 1.1em;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .dataframe thead tr th {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            padding: 18px !important;
            text-align: center !important;
            border: none !important;
            letter-spacing: 0.5px;
        }
        .dataframe tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .dataframe tbody tr:nth-child(odd) {
            background-color: white;
        }
        .dataframe tbody tr:hover {
            background-color: #e3f2fd !important;
            transition: background-color 0.2s;
        }
        .dataframe tbody tr:last-child {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
            font-weight: 800 !important;
            font-size: 1.15em !important;
            border-top: 4px solid #e17055 !important;
        }
        .dataframe tbody tr:last-child:hover {
            background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%) !important;
        }
        .dataframe td {
            padding: 14px !important;
            border-bottom: 1px solid #dee2e6 !important;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.8em !important;
            font-weight: 700 !important;
            color: #2c3e50 !important;
            margin-top: 25px !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Full-width header banner
    st.markdown("""
        <div class="header-banner">
            <h1 class="header-title">EK PED MAA KE NAAM 2.0</h1>
            <p class="header-subtitle">UP Secondary Schools Eco Club Monitoring Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load cached data
    with st.spinner("Loading data..."):
        df, success, error_message, data_service = load_eco_data()
    with st.spinner("Loading data..."):
        df, success, error_message = data_service.load_data()
    
    # Handle data loading errors
    if not success:
        st.error(f"❌ {error_message}")
        st.info("Please ensure the following files exist in the project folder:")
        st.markdown("- School Master.xlsx")
        st.markdown("- All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        st.markdown("- UTTAR PRADESH.xlsx")
        return
    
    # Display summary metrics with colorful cards
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    # Custom CSS for colorful metric cards and table styling
    st.markdown("""
        <style>
        .metric-card {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin: 10px 0;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-icon {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 0.95em;
            color: #666;
            font-weight: 500;
        }
        .blue-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .blue-card .metric-label { color: #f0f0f0; }
        .green-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .green-card .metric-label { color: #f0f0f0; }
        .red-card {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
            color: white;
        }
        .red-card .metric-label { color: #f0f0f0; }
        .light-green-card {
            background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);
            color: white;
        }
        .light-green-card .metric-label { color: #f0f0f0; }
        .orange-card {
            background: linear-gradient(135deg, #f46b45 0%, #eea849 100%);
            color: white;
        }
        .orange-card .metric-label { color: #f0f0f0; }
        .dark-green-card {
            background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
            color: white;
        }
        .dark-green-card .metric-label { color: #f0f0f0; }
        
        /* Filter Section */
        .filter-container {
            background: linear-gradient(135deg, #e8f4f8 0%, #d6e9f5 100%);
            padding: 30px;
            border-radius: 15px;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(70, 130, 180, 0.15);
            border: 2px solid #b3d9f2;
        }
        .filter-header {
            font-size: 1.4em;
            font-weight: 700;
            color