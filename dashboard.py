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
        
        .header-banner::before {
            content: '🌳';
            position: absolute;
            left: 30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3.5em;
            opacity: 0.9;
        }
        
        .header-banner::after {
            content: '🇮🇳';
            position: absolute;
            right: 30px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 3.5em;
            opacity: 0.9;
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
    
    # Create 6 column layout
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card blue-card">
                <div class="metric-icon">🏫</div>
                <div class="metric-value">{total_schools:,}</div>
                <div class="metric-label">Total Schools</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card green-card">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{notif_uploaded:,}</div>
                <div class="metric-label">Notification Uploaded</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card red-card">
                <div class="metric-icon">❌</div>
                <div class="metric-value">{notif_not_uploaded:,}</div>
                <div class="metric-label">NOT Uploaded</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card light-green-card">
                <div class="metric-icon">🌳</div>
                <div class="metric-value">{tree_uploaded:,}</div>
                <div class="metric-label">Tree Uploaded Schools</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
            <div class="metric-card orange-card">
                <div class="metric-icon">⚠️</div>
                <div class="metric-value">{tree_not_uploaded:,}</div>
                <div class="metric-label">Tree NOT Uploaded</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
            <div class="metric-card dark-green-card">
                <div class="metric-icon">🌲</div>
                <div class="metric-value">{total_trees:,}</div>
                <div class="metric-label">Total Trees</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Notification Report", "🌳 Tree Planted Report", "📊 Summary Report"])
    
    # Tab 1: Notification Report
    with tab1:
        st.subheader("Notification Upload Status")
        
        # Filters for Notification Report wrapped in styled container
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.markdown('<div class="filter-header"><span>🔍</span> Filter Options</div>', unsafe_allow_html=True)
        
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        
        with col_f1:
            st.markdown('<label class="filter-label">District:</label>', unsafe_allow_html=True)
            # District filter
            districts = sorted(df['District'].unique().tolist())
            district_options = ["All"] + districts
            selected_district = st.selectbox(
                "Select District",
                options=district_options,
                index=0,
                key="notif_district",
                label_visibility="collapsed"
            )
        
        with col_f2:
            st.markdown('<label class="filter-label">School Type:</label>', unsafe_allow_html=True)
            # School Management filter
            school_type_options = ["All", "Private Unaided Recognized", "Government Aided", 
                                  "Department of Education (Government School)"]
            selected_school_type = st.selectbox(
                "Select School Type",
                options=school_type_options,
                index=0,
                key="notif_school_type",
                label_visibility="collapsed"
            )
        
        with col_f3:
            st.markdown('<label class="filter-label">Status:</label>', unsafe_allow_html=True)
            # Notification Status filter
            notif_filter_options = ["All", "Uploaded", "NOT Uploaded"]
            selected_notif_filter = st.selectbox(
                "Notification Status",
                options=notif_filter_options,
                index=0,
                key="notif_status_filter",
                label_visibility="collapsed"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters - separate for metrics and table display
        with st.spinner('Applying filters...'):
            # For metrics: only district and school type filter (not status)
            notif_base_df = df.copy()
            
            if selected_district != "All":
                notif_base_df = notif_base_df[notif_base_df['District'] == selected_district]
            
            if selected_school_type != "All":
                notif_base_df = notif_base_df[notif_base_df['School Management'] == selected_school_type]
            
            # For table display: apply all filters including status
            notif_filtered_df = notif_base_df.copy()
            
            if selected_notif_filter == "Uploaded":
                notif_filtered_df = notif_filtered_df[notif_filtered_df['Notification Uploaded'] == 'Yes']
            elif selected_notif_filter == "NOT Uploaded":
                notif_filtered_df = notif_filtered_df[notif_filtered_df['Notification Uploaded'] == 'No']
        
        # Notification metrics - calculated from base filter (district + school type only)
        notif_total = len(notif_base_df)
        notif_uploaded_count = len(notif_base_df[notif_base_df['Notification Uploaded'] == 'Yes'])
        notif_not_uploaded_count = len(notif_base_df[notif_base_df['Notification Uploaded'] == 'No'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card blue-card">
                    <div class="metric-icon">🏫</div>
                    <div class="metric-value">{notif_total:,}</div>
                    <div class="metric-label">Total Schools</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card green-card">
                    <div class="metric-icon">✅</div>
                    <div class="metric-value">{notif_uploaded_count:,}</div>
                    <div class="metric-label">Notification Uploaded</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card red-card">
                    <div class="metric-icon">❌</div>
                    <div class="metric-value">{notif_not_uploaded_count:,}</div>
                    <div class="metric-label">Notification NOT Uploaded</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.info(f"📊 **Showing {len(notif_filtered_df):,} schools** in the table below based on selected filters. Metrics above show complete totals for selected District & School Type.")
        
        # School Type wise Notification Summary Table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h2 style="font-size: 2em; font-weight: 700; color: #000000; margin-bottom: 20px;">📊 School Type-wise Notification Summary</h2>', unsafe_allow_html=True)
        
        # Calculate summary by school type (using base df which has district + school type filters)
        school_type_summary = notif_base_df.groupby('School Management').agg({
            'UDISE Code': 'count',
            'Notification Uploaded': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        school_type_summary.columns = ['School Type', 'Total Schools', 'Notification Uploaded']
        
        # Add Notification NOT Uploaded column
        school_type_summary['Notification NOT Uploaded'] = school_type_summary['Total Schools'] - school_type_summary['Notification Uploaded']
        
        # Add Sr. No.
        school_type_summary.insert(0, 'Sr. No.', range(1, len(school_type_summary) + 1))
        
        # Add TOTAL row
        total_row_notif = pd.DataFrame({
            'Sr. No.': [0],
            'School Type': ['TOTAL'],
            'Total Schools': [school_type_summary['Total Schools'].sum()],
            'Notification Uploaded': [school_type_summary['Notification Uploaded'].sum()],
            'Notification NOT Uploaded': [school_type_summary['Notification NOT Uploaded'].sum()]
        })
        school_type_summary_with_total = pd.concat([school_type_summary, total_row_notif], ignore_index=True)
        
        # Custom styling for the summary table
        def style_summary_table(df):
            return df.style.set_table_styles([
                # Header styling
                {
                    'selector': 'thead th',
                    'props': [
                        ('background-color', '#2c5aa0'),
                        ('color', 'white'),
                        ('font-weight', '900'),
                        ('text-align', 'center'),
                        ('padding', '14px'),
                        ('border', '1px solid #1e4a7a'),
                        ('font-size', '1.15em'),
                        ('text-transform', 'uppercase'),
                        ('letter-spacing', '0.5px')
                    ]
                },
                # All cells
                {
                    'selector': 'td',
                    'props': [
                        ('border', '1px solid #ddd'),
                        ('padding', '10px'),
                        ('text-align', 'left')
                    ]
                },
                # Number columns (right align)
                {
                    'selector': 'td:nth-child(n+3)',
                    'props': [
                        ('text-align', 'right')
                    ]
                },
                # Zebra striping
                {
                    'selector': 'tbody tr:nth-child(even)',
                    'props': [
                        ('background-color', '#f8f9fa')
                    ]
                },
                {
                    'selector': 'tbody tr:nth-child(odd)',
                    'props': [
                        ('background-color', 'white')
                    ]
                },
                # TOTAL row
                {
                    'selector': 'tbody tr:last-child',
                    'props': [
                        ('background-color', '#ff9800 !important'),
                        ('color', 'white'),
                        ('font-weight', '900'),
                        ('font-size', '1.15em'),
                        ('border-top', '3px solid #e68900'),
                        ('border-bottom', '3px solid #e68900')
                    ]
                },
                # Hover effect
                {
                    'selector': 'tbody tr:hover',
                    'props': [
                        ('background-color', '#e3f2fd !important')
                    ]
                }
            ]).set_properties(**{
                'text-align': 'center'
            }, subset=['Sr. No.']).set_properties(**{
                'text-align': 'right'
            }, subset=['Total Schools', 'Notification Uploaded', 'Notification NOT Uploaded']).hide(axis='index')
        
        # Display the summary table
        st.dataframe(
            style_summary_table(school_type_summary_with_total),
            use_container_width=True,
        )
        
        st.markdown("---")
        
        # Display notification data with enhanced styling
        notif_df = notif_filtered_df[['District', 'School Name', 'UDISE Code', 'School Management', 
                                      'School Category', 'Notification Uploaded']].copy()
        
        # Apply color coding to Status column
        def highlight_status(row):
            if row['Notification Uploaded'] == 'Yes':
                return [''] * 5 + ['background-color: #d4edda; color: #155724; font-weight: bold']
            else:
                return [''] * 5 + ['background-color: #f8d7da; color: #721c24; font-weight: bold']
        
        styled_notif_df = notif_df.style.apply(highlight_status, axis=1).set_table_styles([
            {
                'selector': 'thead th',
                'props': [
                    ('background-color', '#1a252f'),
                    ('color', 'white'),
                    ('font-weight', '900'),
                    ('text-align', 'center'),
                    ('padding', '14px'),
                    ('position', 'sticky'),
                    ('top', '0'),
                    ('z-index', '1'),
                    ('border', '1px solid #0d1419'),
                    ('font-size', '1.05em'),
                    ('text-transform', 'uppercase'),
                    ('letter-spacing', '0.5px')
                ]
            },
            {
                'selector': 'tbody tr:hover',
                'props': [
                    ('background-color', '#e3f2fd'),
                    ('cursor', 'pointer')
                ]
            },
            {
                'selector': 'td',
                'props': [
                    ('padding', '10px'),
                    ('border', '1px solid #ddd')
                ]
            }
        ])
        
        st.dataframe(
            styled_notif_df,
            column_config={
                "District": st.column_config.TextColumn("District", width="medium"),
                "School Name": st.column_config.TextColumn("School Name", width="large"),
                "UDISE Code": st.column_config.TextColumn("UDISE Code", width="medium"),
                "School Management": st.column_config.TextColumn("School Type", width="medium"),
                "School Category": st.column_config.TextColumn("Category", width="medium"),
                "Notification Uploaded": st.column_config.TextColumn("Status", width="small"),
            },
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Download button
        st.download_button(
            label="📥 Download Filtered Report",
            data=notif_df.to_csv(index=False).encode('utf-8'),
            file_name=f"notification_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_notif"
        )
    
    # Tab 2: Tree Planted Report
    with tab2:
        st.subheader("Tree Plantation Status")
        
        # Filters for Tree Report wrapped in styled container
        st.markdown('<div class="filter-container">', unsafe_allow_html=True)
        st.markdown('<div class="filter-header"><span>🔍</span> Filter Options</div>', unsafe_allow_html=True)
        
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        
        with col_f1:
            st.markdown('<label class="filter-label">District:</label>', unsafe_allow_html=True)
            # District filter
            districts_tree = sorted(df['District'].unique().tolist())
            district_options_tree = ["All"] + districts_tree
            selected_district_tree = st.selectbox(
                "Select District",
                options=district_options_tree,
                index=0,
                key="tree_district",
                label_visibility="collapsed"
            )
        
        with col_f2:
            st.markdown('<label class="filter-label">School Type:</label>', unsafe_allow_html=True)
            # School Management filter
            school_type_options_tree = ["All", "Private Unaided Recognized", "Government Aided", 
                                       "Department of Education (Government School)"]
            selected_school_type_tree = st.selectbox(
                "Select School Type",
                options=school_type_options_tree,
                index=0,
                key="tree_school_type",
                label_visibility="collapsed"
            )
        
        with col_f3:
            st.markdown('<label class="filter-label">Status:</label>', unsafe_allow_html=True)
            # Tree Status filter
            tree_filter_options = ["All", "Uploaded", "NOT Uploaded"]
            selected_tree_filter = st.selectbox(
                "Tree Status",
                options=tree_filter_options,
                index=0,
                key="tree_status_filter",
                label_visibility="collapsed"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Apply filters - separate for metrics and table display
        with st.spinner('Applying filters...'):
            # For metrics: only district and school type filter (not status)
            tree_base_df = df.copy()
            
            if selected_district_tree != "All":
                tree_base_df = tree_base_df[tree_base_df['District'] == selected_district_tree]
            
            if selected_school_type_tree != "All":
                tree_base_df = tree_base_df[tree_base_df['School Management'] == selected_school_type_tree]
            
            # For table display: apply all filters including status
            tree_filtered_df = tree_base_df.copy()
            
            if selected_tree_filter == "Uploaded":
                tree_filtered_df = tree_filtered_df[tree_filtered_df['Tree Uploaded'] == 'Yes']
            elif selected_tree_filter == "NOT Uploaded":
                tree_filtered_df = tree_filtered_df[tree_filtered_df['Tree Uploaded'] == 'No']
        
        # Tree metrics - calculated from base filter (district + school type only)
        tree_total = len(tree_base_df)
        tree_uploaded_count = len(tree_base_df[tree_base_df['Tree Uploaded'] == 'Yes'])
        tree_not_uploaded_count = len(tree_base_df[tree_base_df['Tree Uploaded'] == 'No'])
        tree_total_trees = tree_base_df['Trees Planted'].sum()
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.metric("Total Schools", f"{tree_total:,}")
        with col2:
            st.metric("✅ Tree Uploaded", f"{tree_uploaded_count:,}")
        with col3:
            st.metric("❌ Tree NOT Uploaded", f"{tree_not_uploaded_count:,}")
        with col4:
            st.metric("🌳 Total Trees Planted", f"{tree_total_trees:,}")
        
        st.info(f"📊 **Showing {len(tree_filtered_df):,} schools** in the table below based on selected filters. Metrics above show complete totals for selected District & School Type.")
        st.markdown("---")
        
        # School Type wise Tree Plantation Summary Table
        st.markdown("#### 🌳 School Type-wise Tree Plantation Summary")
        
        # Calculate summary by school type (using base df which has district + school type filters)
        tree_type_summary = tree_base_df.groupby('School Management').agg({
            'UDISE Code': 'count',
            'Tree Uploaded': lambda x: (x == 'Yes').sum(),
            'Trees Planted': 'sum'
        }).reset_index()
        
        tree_type_summary.columns = ['School Type', 'Total Schools', 'Schools with Tree Upload', 'Total Trees Planted']
        
        # Add Schools with NO Tree Upload column
        tree_type_summary['Schools with NO Tree Upload'] = tree_type_summary['Total Schools'] - tree_type_summary['Schools with Tree Upload']
        
        # Add Sr. No.
        tree_type_summary.insert(0, 'Sr. No.', range(1, len(tree_type_summary) + 1))
        
        # Add TOTAL row
        total_row_tree = pd.DataFrame({
            'Sr. No.': [0],
            'School Type': ['TOTAL'],
            'Total Schools': [tree_type_summary['Total Schools'].sum()],
            'Schools with Tree Upload': [tree_type_summary['Schools with Tree Upload'].sum()],
            'Schools with NO Tree Upload': [tree_type_summary['Schools with NO Tree Upload'].sum()],
            'Total Trees Planted': [tree_type_summary['Total Trees Planted'].sum()]
        })
        tree_type_summary_with_total = pd.concat([tree_type_summary, total_row_tree], ignore_index=True)
        
        # Display the summary table
        st.dataframe(
            tree_type_summary_with_total,
            column_config={
                "Sr. No.": st.column_config.TextColumn("Sr. No.", width="small"),
                "School Type": st.column_config.TextColumn("School Type", width="large"),
                "Total Schools": st.column_config.NumberColumn("Total Schools", width="medium", format="%d"),
                "Schools with Tree Upload": st.column_config.NumberColumn("Schools with Tree Upload", width="medium", format="%d"),
                "Schools with NO Tree Upload": st.column_config.NumberColumn("Schools with NO Tree Upload", width="medium", format="%d"),
                "Total Trees Planted": st.column_config.NumberColumn("Total Trees Planted", width="medium", format="%d"),
            },
            use_container_width=True,
            hide_index=True,
        )
        
        st.markdown("---")
        
        # Display tree data
        tree_df = tree_filtered_df[['District', 'School Name', 'UDISE Code', 'School Management',
                                     'School Category', 'Trees Planted', 'Tree Uploaded']].copy()
        
        st.dataframe(
            tree_df,
            column_config={
                "District": st.column_config.TextColumn("District", width="medium"),
                "School Name": st.column_config.TextColumn("School Name", width="large"),
                "UDISE Code": st.column_config.TextColumn("UDISE Code", width="medium"),
                "School Management": st.column_config.TextColumn("School Type", width="medium"),
                "School Category": st.column_config.TextColumn("Category", width="medium"),
                "Trees Planted": st.column_config.NumberColumn("Trees Planted", width="small", format="%d"),
                "Tree Uploaded": st.column_config.TextColumn("Status", width="small"),
            },
            use_container_width=True,
            hide_index=True,
            height=600
        )
        
        # Download button
        st.download_button(
            label="📥 Download Filtered Report",
            data=tree_df.to_csv(index=False).encode('utf-8'),
            file_name=f"tree_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_tree"
        )
    
    # Tab 3: Summary Report
    with tab3:
        st.subheader("📊 Summary Reports")
        
        # 1. District-wise Summary Report
        st.markdown("### 📍 District-wise Summary Report")
        
        # Calculate district-wise statistics
        district_summary = df.groupby('District').agg({
            'UDISE Code': 'count',
            'Notification Uploaded': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        district_summary.columns = ['District', 'Total Schools', 'Eco-Club Notification Uploaded']
        district_summary['Percentage (%)'] = (
            (district_summary['Eco-Club Notification Uploaded'] / district_summary['Total Schools'] * 100)
            .round(2)
        )
        
        # Sort by district name
        district_summary = district_summary.sort_values('District')
        
        # Add TOTAL row at the bottom
        total_row = pd.DataFrame({
            'District': ['TOTAL'],
            'Total Schools': [district_summary['Total Schools'].sum()],
            'Eco-Club Notification Uploaded': [district_summary['Eco-Club Notification Uploaded'].sum()],
            'Percentage (%)': [
                (district_summary['Eco-Club Notification Uploaded'].sum() / 
                 district_summary['Total Schools'].sum() * 100).round(2)
            ]
        })
        
        district_summary_with_total = pd.concat([district_summary, total_row], ignore_index=True)
        
        st.dataframe(
            district_summary_with_total,
            column_config={
                "District": st.column_config.TextColumn("District", width="medium"),
                "Total Schools": st.column_config.NumberColumn("Total Schools", width="small", format="%d"),
                "Eco-Club Notification Uploaded": st.column_config.NumberColumn(
                    "Notification Uploaded", 
                    width="small", 
                    format="%d"
                ),
                "Percentage (%)": st.column_config.NumberColumn(
                    "Percentage (%)", 
                    width="small", 
                    format="%.2f%%"
                ),
            },
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Show overall summary metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("📚 Total Schools", f"{total_row['Total Schools'].iloc[0]:,}")
        with col_m2:
            st.metric("✅ Total Notifications Uploaded", f"{total_row['Eco-Club Notification Uploaded'].iloc[0]:,}")
        with col_m3:
            st.metric("📊 Overall Percentage", f"{total_row['Percentage (%)'].iloc[0]:.2f}%")
        
        # Download button
        st.download_button(
            label="📥 Download District Summary",
            data=district_summary.to_csv(index=False).encode('utf-8'),
            file_name=f"district_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key="download_district_summary"
        )
        
        st.markdown("---")
        
        # 2. Top 10 Best Performing Districts
        st.markdown("### 🏆 Top 10 Best Performing Districts")
        
        top_10 = district_summary.nlargest(10, 'Percentage (%)')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                top_10,
                column_config={
                    "District": st.column_config.TextColumn("District", width="medium"),
                    "Total Schools": st.column_config.NumberColumn("Total Schools", width="small", format="%d"),
                    "Eco-Club Notification Uploaded": st.column_config.NumberColumn(
                        "Uploaded", 
                        width="small", 
                        format="%d"
                    ),
                    "Percentage (%)": st.column_config.NumberColumn(
                        "Percentage (%)", 
                        width="small", 
                        format="%.2f%%"
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            # Show top 3 as metrics
            if len(top_10) >= 3:
                st.metric("🥇 1st Place", top_10.iloc[0]['District'], 
                         f"{top_10.iloc[0]['Percentage (%)']}%")
                st.metric("🥈 2nd Place", top_10.iloc[1]['District'], 
                         f"{top_10.iloc[1]['Percentage (%)']}%")
                st.metric("🥉 3rd Place", top_10.iloc[2]['District'], 
                         f"{top_10.iloc[2]['Percentage (%)']}%")
        
        st.markdown("---")
        
        # 3. Bottom 10 Worst Performing Districts
        st.markdown("### ⚠️ Bottom 10 Districts (Need Attention)")
        
        bottom_10 = district_summary.nsmallest(10, 'Percentage (%)')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.dataframe(
                bottom_10,
                column_config={
                    "District": st.column_config.TextColumn("District", width="medium"),
                    "Total Schools": st.column_config.NumberColumn("Total Schools", width="small", format="%d"),
                    "Eco-Club Notification Uploaded": st.column_config.NumberColumn(
                        "Uploaded", 
                        width="small", 
                        format="%d"
                    ),
                    "Percentage (%)": st.column_config.NumberColumn(
                        "Percentage (%)", 
                        width="small", 
                        format="%.2f%%"
                    ),
                },
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            # Show bottom 3 as warning metrics
            if len(bottom_10) >= 3:
                st.metric("⚠️ Needs Most Attention", bottom_10.iloc[0]['District'], 
                         f"{bottom_10.iloc[0]['Percentage (%)']}%", delta_color="inverse")
                st.metric("⚠️ Second Priority", bottom_10.iloc[1]['District'], 
                         f"{bottom_10.iloc[1]['Percentage (%)']}%", delta_color="inverse")
                st.metric("⚠️ Third Priority", bottom_10.iloc[2]['District'], 
                         f"{bottom_10.iloc[2]['Percentage (%)']}%", delta_color="inverse")
        
        # Combined download for all summary reports
        st.markdown("---")
        
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.download_button(
                label="📥 Download Top 10",
                data=top_10.to_csv(index=False).encode('utf-8'),
                file_name=f"top_10_districts_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_top_10"
            )
        
        with col_d2:
            st.download_button(
                label="📥 Download Bottom 10",
                data=bottom_10.to_csv(index=False).encode('utf-8'),
                file_name=f"bottom_10_districts_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_bottom_10"
            )
        
        with col_d3:
            # Create comprehensive report with totals
            with pd.ExcelWriter('summary_reports.xlsx', engine='openpyxl') as writer:
                district_summary_with_total.to_excel(writer, sheet_name='All Districts', index=False)
                top_10.to_excel(writer, sheet_name='Top 10', index=False)
                bottom_10.to_excel(writer, sheet_name='Bottom 10', index=False)
                
                # Add summary sheet
                summary_sheet = pd.DataFrame({
                    'Metric': ['Total Schools', 'Total Notifications Uploaded', 'Overall Percentage (%)'],
                    'Value': [
                        total_row['Total Schools'].iloc[0],
                        total_row['Eco-Club Notification Uploaded'].iloc[0],
                        total_row['Percentage (%)'].iloc[0]
                    ]
                })
                summary_sheet.to_excel(writer, sheet_name='Overall Summary', index=False)
            
            with open('summary_reports.xlsx', 'rb') as f:
                st.download_button(
                    label="📥 Download Complete Report (Excel)",
                    data=f,
                    file_name=f"complete_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_complete_summary"
                )
    
    # Footer with visitor counter
    st.markdown("---")
    
    # Get visitor count
    total_visits, unique_visitors, active_users = get_visitor_count()
    
    # Footer with stats
    last_update = get_github_last_update()
    st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px;'>
            <p style='margin: 0; color: #666; font-size: 0.9em;'>
                Last updated: {last_update} | Developed by Alok Mohan
            </p>
            <p style='margin: 5px 0 0 0; font-size: 1em; font-weight: 600;'>
                🟢 <span style='color: #4CAF50;'>Active Now: {active_users}</span> | 
                👁️ Total Visits: {total_visits:,} | 
                👥 Unique Visitors: {unique_visitors:,}
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
