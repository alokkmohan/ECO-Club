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


# Page configuration
st.set_page_config(
    page_title="UP Secondary Schools Eco Club Monitoring Dashboard",
    page_icon="🌱",
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
        </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.title("🌱 UP Secondary Schools Eco Club Monitoring Dashboard")
    st.markdown("---")
    
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
    
    # Display summary metrics
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    
    total_schools = len(df)
    notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])
    notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])
    tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])
    total_trees = df['Trees Planted'].sum()
    
    with col1:
        st.metric("Total Schools", f"{total_schools:,}")
    
    with col2:
        st.metric("Notif Uploaded", f"{notif_uploaded:,}")
    
    with col3:
        st.metric("Notif NOT Uploaded", f"{notif_not_uploaded:,}")
    
    with col4:
        st.metric("Tree Uploaded Schools", f"{tree_uploaded:,}")
    
    with col5:
        st.metric("Tree NOT Uploaded Schools", f"{tree_not_uploaded:,}")
    
    with col6:
        st.metric("Total Trees", f"{total_trees:,}")
    
    st.markdown("---")
    
    # Home button
    if st.button("🏠 Home"):
        st.rerun()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Notification Report", "🌳 Tree Planted Report", "📊 Summary Report"])
    
    # Tab 1: Notification Report
    with tab1:
        st.subheader("Notification Upload Status")
        
        # Filters for Notification Report
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        
        with col_f1:
            # District filter
            districts = sorted(df['District'].unique().tolist())
            district_options = ["All"] + districts
            selected_district = st.selectbox(
                "Select District",
                options=district_options,
                index=0,
                key="notif_district"
            )
        
        with col_f2:
            # School Management filter
            school_type_options = ["All", "Private Unaided Recognized", "Government Aided", 
                                  "Department of Education (Government School)"]
            selected_school_type = st.selectbox(
                "Select School Type",
                options=school_type_options,
                index=0,
                key="notif_school_type"
            )
        
        with col_f3:
            # Notification Status filter
            notif_filter_options = ["All", "Uploaded", "NOT Uploaded"]
            selected_notif_filter = st.selectbox(
                "Notification Status",
                options=notif_filter_options,
                index=0,
                key="notif_status_filter"
            )
        
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
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Total Schools", f"{notif_total:,}")
        with col2:
            st.metric("✅ Notification Uploaded", f"{notif_uploaded_count:,}")
        with col3:
            st.metric("❌ Notification NOT Uploaded", f"{notif_not_uploaded_count:,}")
        
        # School Type-wise Notification Summary Table
        st.markdown("---")
        st.subheader("School Type-wise Notification Summary")
        
        school_type_summary = notif_base_df.groupby('School Management').agg({
            'School Name': 'count',
            'Notification Uploaded': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        school_type_summary.columns = ['School Type', 'Total Schools', 'Notification Uploaded']
        school_type_summary['Notification NOT Uploaded'] = school_type_summary['Total Schools'] - school_type_summary['Notification Uploaded']
        school_type_summary.insert(0, 'Sr. No.', range(1, len(school_type_summary) + 1))
        
        total_row_notif = pd.DataFrame({
            'Sr. No.': [0],
            'School Type': ['TOTAL'],
            'Total Schools': [school_type_summary['Total Schools'].sum()],
            'Notification Uploaded': [school_type_summary['Notification Uploaded'].sum()],
            'Notification NOT Uploaded': [school_type_summary['Notification NOT Uploaded'].sum()]
        })
        school_type_summary_with_total = pd.concat([school_type_summary, total_row_notif], ignore_index=True)
        
        st.dataframe(
            school_type_summary_with_total,
            column_config={
                "Sr. No.": st.column_config.TextColumn("Sr. No.", width="small"),
                "School Type": st.column_config.TextColumn("School Type", width="large"),
                "Total Schools": st.column_config.NumberColumn("Total Schools", width="medium", format="%d"),
                "Notification Uploaded": st.column_config.NumberColumn("Notification Uploaded", width="medium", format="%d"),
                "Notification NOT Uploaded": st.column_config.NumberColumn("Notification NOT Uploaded", width="medium", format="%d"),
            },
            use_container_width=True,
            hide_index=True,
        )
        
        st.markdown("---")
        st.markdown("### 📋 Detailed School-wise Data")

        
        
        st.info(f"📊 **Showing {len(notif_filtered_df):,} schools** in the table below based on selected filters. Metrics above show complete totals for selected District & School Type.")
        st.markdown("---")
        
        # Display notification data
        notif_df = notif_filtered_df[['District', 'School Name', 'UDISE Code', 'School Management', 
                                      'School Category', 'Notification Uploaded']].copy()
        
        st.dataframe(
            notif_df,
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
        
        # Filters for Tree Report
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        
        with col_f1:
            # District filter
            districts_tree = sorted(df['District'].unique().tolist())
            district_options_tree = ["All"] + districts_tree
            selected_district_tree = st.selectbox(
                "Select District",
                options=district_options_tree,
                index=0,
                key="tree_district"
            )
        
        with col_f2:
            # School Management filter
            school_type_options_tree = ["All", "Private Unaided Recognized", "Government Aided", 
                                       "Department of Education (Government School)"]
            selected_school_type_tree = st.selectbox(
                "Select School Type",
                options=school_type_options_tree,
                index=0,
                key="tree_school_type"
            )
        
        with col_f3:
            # Tree Status filter
            tree_filter_options = ["All", "Uploaded", "NOT Uploaded"]
            selected_tree_filter = st.selectbox(
                "Tree Status",
                options=tree_filter_options,
                index=0,
                key="tree_status_filter"
            )
        
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
        
        # School Type-wise Tree Plantation Summary Table
        st.markdown("---")
        st.subheader("School Type-wise Tree Plantation Summary")
        
        tree_type_summary = tree_base_df.groupby('School Management').agg({
            'School Name': 'count',
            'Tree Uploaded': lambda x: (x == 'Yes').sum(),
            'Trees Planted': 'sum'
        }).reset_index()
        
        tree_type_summary.columns = ['School Type', 'Total Schools', 'Schools with Tree Upload', 'Total Trees Planted']
        tree_type_summary['Schools with NO Tree Upload'] = tree_type_summary['Total Schools'] - tree_type_summary['Schools with Tree Upload']
        tree_type_summary.insert(0, 'Sr. No.', range(1, len(tree_type_summary) + 1))
        
        total_row_tree = pd.DataFrame({
            'Sr. No.': [0],
            'School Type': ['TOTAL'],
            'Total Schools': [tree_type_summary['Total Schools'].sum()],
            'Schools with Tree Upload': [tree_type_summary['Schools with Tree Upload'].sum()],
            'Schools with NO Tree Upload': [tree_type_summary['Schools with NO Tree Upload'].sum()],
            'Total Trees Planted': [tree_type_summary['Total Trees Planted'].sum()]
        })
        tree_type_summary_with_total = pd.concat([tree_type_summary, total_row_tree], ignore_index=True)
        
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
        st.markdown("### 🌳 Detailed School-wise Data")

        
        
        st.info(f"📊 **Showing {len(tree_filtered_df):,} schools** in the table below based on selected filters. Metrics above show complete totals for selected District & School Type.")
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

        

        # Section 1: Charts Only (Visual Status)

        col_chart1, col_chart2 = st.columns(2)

        

        with col_chart1:

            st.markdown("#### 📋 Notification Upload Status")

            notif_uploaded = len(df[df['Notification Uploaded'] == 'Yes'])

            notif_not_uploaded = len(df[df['Notification Uploaded'] == 'No'])

            

            import plotly.graph_objects as go

            

            fig_notif = go.Figure(data=[go.Pie(

                labels=['Uploaded', 'Not Uploaded'],

                values=[notif_uploaded, notif_not_uploaded],

                hole=.4,

                marker_colors=['#4CAF50', '#f44336'],

                textinfo='label+percent',

                textfont_size=14

            )])

            

            fig_notif.update_layout(

                showlegend=True,

                height=400,

                margin=dict(t=50, b=50, l=50, r=50),

                annotations=[dict(

                    text=f'{(notif_uploaded/(notif_uploaded+notif_not_uploaded)*100):.1f}%',

                    x=0.5, y=0.5, font_size=24, showarrow=False

                )]

            )

            

            st.plotly_chart(fig_notif, use_container_width=True)

        

        with col_chart2:

            st.markdown("#### 🌳 Tree Plantation Status")

            tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])

            tree_not_uploaded = len(df[df['Tree Uploaded'] == 'No'])

            

            fig_tree = go.Figure(data=[go.Pie(

                labels=['Uploaded', 'Not Uploaded'],

                values=[tree_uploaded, tree_not_uploaded],

                hole=.4,

                marker_colors=['#4CAF50', '#f44336'],

                textinfo='label+percent',

                textfont_size=14

            )])

            

            fig_tree.update_layout(

                showlegend=True,

                height=400,

                margin=dict(t=50, b=50, l=50, r=50),

                annotations=[dict(

                    text=f'{(tree_uploaded/(tree_uploaded+tree_not_uploaded)*100):.1f}%',

                    x=0.5, y=0.5, font_size=24, showarrow=False

                )]

            )

            

            st.plotly_chart(fig_tree, use_container_width=True)

        

        # Divider between charts and statistics

        st.divider()

        

        # Section 2: Overall Statistics (Numbers Only)

        st.markdown("### 📊 Overall Statistics")

        

        # Calculate metrics

        total_schools = len(df)

        total_trees = df['Trees Planted'].sum()

        notif_percentage = (notif_uploaded / total_schools * 100)

        tree_percentage = (tree_uploaded / total_schools * 100)

        

        # Display KPI cards

        col_k1, col_k2, col_k3, col_k4, col_k5 = st.columns(5)

        

        with col_k1:

            st.metric(

                "📚 Total Schools",

                f"{total_schools:,}",

                help="Total number of schools in the system"

            )

        

        with col_k2:

            st.metric(

                "✅ Notification Uploaded",

                f"{notif_uploaded:,}",

                delta=f"{notif_percentage:.1f}%",

                help="Schools that uploaded notifications"

            )

        

        with col_k3:

            st.metric(

                "❌ Notification NOT Uploaded",

                f"{notif_not_uploaded:,}",

                delta=f"{(100-notif_percentage):.1f}%",

                delta_color="inverse",

                help="Schools that did not upload notifications"

            )

        

        with col_k4:

            st.metric(

                "✅ Tree Data Uploaded",

                f"{tree_uploaded:,}",

                delta=f"{tree_percentage:.1f}%",

                help="Schools that uploaded tree data"

            )

        

        with col_k5:

            st.metric(

                "❌ Tree NOT Uploaded",

                f"{tree_not_uploaded:,}",

                delta=f"{(100-tree_percentage):.1f}%",

                delta_color="inverse",

                help="Schools that did not upload tree data"

            )

        

        # Second row of metrics

        col_k6, col_k7, col_k8, col_k9, col_k10 = st.columns(5)

        

        with col_k6:

            st.metric(

                "🌱 Total Trees Planted",

                f"{total_trees:,}",

                help="Total number of trees planted across all schools"

            )

        

        with col_k7:

            st.metric(

                "📊 Overall Notification Rate",

                f"{notif_percentage:.1f}%",

                help="Percentage of schools with notifications"

            )

        

        with col_k8:

            st.metric(

                "📊 Overall Tree Upload Rate",

                f"{tree_percentage:.1f}%",

                help="Percentage of schools with tree data"

            )

        

        with col_k9:

            avg_trees = int(total_trees / tree_uploaded) if tree_uploaded > 0 else 0

            st.metric(

                "🌳 Avg Trees per School",

                f"{avg_trees:,}",

                help="Average trees planted per school (among uploaders)"

            )

        

        with col_k10:

            both_uploaded = len(df[(df['Notification Uploaded'] == 'Yes') & (df['Tree Uploaded'] == 'Yes')])

            compliance_rate = (both_uploaded / total_schools * 100)

            st.metric(

                "✅ Full Compliance",

                f"{compliance_rate:.1f}%",

                delta=f"{both_uploaded:,} schools",

                help="Schools that completed both notification and tree upload"

            )

        

        # Divider before district reports

        st.divider()
    
    # Footer with visitor counter
    st.markdown("---")
    
    # Get visitor count
    total_visits, unique_visitors, active_users = get_visitor_count()
    
    # Footer with stats
    st.markdown(f"""
        <div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px;'>
            <p style='margin: 0; color: #666; font-size: 0.9em;'>
                Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | Developed by Alok Mohan
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
