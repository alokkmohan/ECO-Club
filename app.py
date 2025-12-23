"""
Eco Club Monitoring Dashboard
A read-only Streamlit dashboard for monitoring school notification uploads.
"""

import streamlit as st
import pandas as pd
from data_service import DataService


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


@st.cache_data(ttl=600, show_spinner=False)  # Cache for 10 minutes
def load_eco_data():
    """Load and cache data."""
    data_service = DataService(data_folder=".")
    df, success, error_message = data_service.load_data()
    return df, success, error_message, data_service


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
        
        # Apply filters
        with st.spinner('Applying filters...'):
            notif_filtered_df = df.copy()
            
            if selected_district != "All":
                notif_filtered_df = notif_filtered_df[notif_filtered_df['District'] == selected_district]
            
            if selected_school_type != "All":
                notif_filtered_df = notif_filtered_df[notif_filtered_df['School Management'] == selected_school_type]
            
            if selected_notif_filter == "Uploaded":
                notif_filtered_df = notif_filtered_df[notif_filtered_df['Notification Uploaded'] == 'Yes']
            elif selected_notif_filter == "NOT Uploaded":
                notif_filtered_df = notif_filtered_df[notif_filtered_df['Notification Uploaded'] == 'No']
        
        # Notification metrics
        notif_total = len(notif_filtered_df)
        notif_uploaded_count = len(notif_filtered_df[notif_filtered_df['Notification Uploaded'] == 'Yes'])
        notif_not_uploaded_count = len(notif_filtered_df[notif_filtered_df['Notification Uploaded'] == 'No'])
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.metric("Total Schools", f"{notif_total:,}")
        with col2:
            st.metric("Notification Uploaded", f"{notif_uploaded_count:,}")
        with col3:
            st.metric("Notification NOT Uploaded", f"{notif_not_uploaded_count:,}")
        
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
        
        # Apply filters
        with st.spinner('Applying filters...'):
            tree_filtered_df = df.copy()
            
            if selected_district_tree != "All":
                tree_filtered_df = tree_filtered_df[tree_filtered_df['District'] == selected_district_tree]
            
            if selected_school_type_tree != "All":
                tree_filtered_df = tree_filtered_df[tree_filtered_df['School Management'] == selected_school_type_tree]
            
            if selected_tree_filter == "Uploaded":
                tree_filtered_df = tree_filtered_df[tree_filtered_df['Tree Uploaded'] == 'Yes']
            elif selected_tree_filter == "NOT Uploaded":
                tree_filtered_df = tree_filtered_df[tree_filtered_df['Tree Uploaded'] == 'No']
        
        # Tree metrics
        tree_total = len(tree_filtered_df)
        tree_uploaded_count = len(tree_filtered_df[tree_filtered_df['Tree Uploaded'] == 'Yes'])
        tree_not_uploaded_count = len(tree_filtered_df[tree_filtered_df['Tree Uploaded'] == 'No'])
        tree_total_trees = tree_filtered_df['Trees Planted'].sum()
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.metric("Total Schools", f"{tree_total:,}")
        with col2:
            st.metric("Tree Uploaded", f"{tree_uploaded_count:,}")
        with col3:
            st.metric("Tree NOT Uploaded", f"{tree_not_uploaded_count:,}")
        with col4:
            st.metric("Total Trees Planted", f"{tree_total_trees:,}")
        
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
        
        st.dataframe(
            district_summary,
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
            # Create comprehensive report
            with pd.ExcelWriter('summary_reports.xlsx', engine='openpyxl') as writer:
                district_summary.to_excel(writer, sheet_name='All Districts', index=False)
                top_10.to_excel(writer, sheet_name='Top 10', index=False)
                bottom_10.to_excel(writer, sheet_name='Bottom 10', index=False)
            
            with open('summary_reports.xlsx', 'rb') as f:
                st.download_button(
                    label="📥 Download Complete Report (Excel)",
                    data=f,
                    file_name=f"complete_summary_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_complete_summary"
                )
    
    # Footer
    st.markdown("---")
    st.caption(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')} | Developed by Alok Mohan")


if __name__ == "__main__":
    main()
