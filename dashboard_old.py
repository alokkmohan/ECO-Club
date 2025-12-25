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
    page_title="Eco Club Dashboard - Uttar Pradesh",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None

# Load data
@st.cache_data
def load_data():
    data_service = DataService(".")
    df, success, error = data_service.load_data()
    return df, success, error, data_service

# Title
st.title("🌳 Eco Club Dashboard - Uttar Pradesh")
st.markdown("---")

# Load data with spinner
with st.spinner('Loading data...'):
    df, success, error, data_service = load_data()

if not success:
    st.error(f"❌ {error}")
    st.stop()

st.session_state.data_loaded = True
st.session_state.df = df

# Sidebar filters
st.sidebar.header("🔍 Filters")

# District filter
districts = ["All"] + data_service.get_districts(df)
selected_district = st.sidebar.selectbox("Select District", districts)

# School filter (dynamic based on district)
if selected_district != "All":
    schools = ["All"] + data_service.get_schools_by_district(df, selected_district)
    selected_school = st.sidebar.selectbox("Select School", schools)
else:
    selected_school = "All"

# School category filter
school_categories = ["All", "Secondary"]
selected_category = st.sidebar.selectbox("School Category", school_categories)

# Notification status filter
notif_options = ["All", "Notification Uploaded", "Notification NOT Uploaded"]
selected_notif = st.sidebar.selectbox("Notification Status", notif_options)

# Tree status filter
tree_options = ["All", "Tree Uploaded", "Tree NOT Uploaded"]
selected_tree = st.sidebar.selectbox("Tree Status", tree_options)

# Apply filters
filtered_df = data_service.filter_data(
    df, 
    selected_district, 
    selected_school, 
    selected_category,
    selected_notif,
    selected_tree
)

# Key Metrics
st.header("📊 Key Statistics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Schools", f"{len(filtered_df):,}")
    
with col2:
    notif_uploaded = (filtered_df['Notification Uploaded'] == 'Yes').sum()
    notif_pct = (notif_uploaded / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Notifications Uploaded", f"{notif_uploaded:,}", f"{notif_pct:.1f}%")
    
with col3:
    tree_uploaded = (filtered_df['Tree Uploaded'] == 'Yes').sum()
    tree_pct = (tree_uploaded / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric("Tree Data Uploaded", f"{tree_uploaded:,}", f"{tree_pct:.1f}%")
    
with col4:
    total_trees = filtered_df['Trees Planted'].sum()
    st.metric("Total Trees Planted", f"{total_trees:,}")

st.markdown("---")

# Charts section
st.header("📈 Analytics")

# Create two columns for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Notification Upload Status")
    notif_counts = filtered_df['Notification Uploaded'].value_counts()
    fig_notif = px.pie(
        values=notif_counts.values,
        names=notif_counts.index,
        color=notif_counts.index,
        color_discrete_map={'Yes': '#10b981', 'No': '#ef4444'},
        hole=0.4
    )
    fig_notif.update_traces(textposition='inside', textinfo='percent+label')
    fig_notif.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_notif, use_container_width=True)

with chart_col2:
    st.subheader("Tree Data Upload Status")
    tree_counts = filtered_df['Tree Uploaded'].value_counts()
    fig_tree = px.pie(
        values=tree_counts.values,
        names=tree_counts.index,
        color=tree_counts.index,
        color_discrete_map={'Yes': '#10b981', 'No': '#ef4444'},
        hole=0.4
    )
    fig_tree.update_traces(textposition='inside', textinfo='percent+label')
    fig_tree.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_tree, use_container_width=True)

# District-wise analysis (only if "All" districts selected)
if selected_district == "All":
    st.subheader("🏛️ District-wise Analysis")
    
    # Group by district
    district_stats = filtered_df.groupby('District').agg({
        'UDISE Code': 'count',
        'Trees Planted': 'sum',
        'Notification Uploaded': lambda x: (x == 'Yes').sum(),
        'Tree Uploaded': lambda x: (x == 'Yes').sum()
    }).reset_index()
    
    district_stats.columns = ['District', 'Total Schools', 'Trees Planted', 
                              'Notifications Uploaded', 'Tree Data Uploaded']
    
    # Sort by total schools
    district_stats = district_stats.sort_values('Total Schools', ascending=False)
    
    # Top 10 districts by schools
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.subheader("Top 10 Districts by Schools")
        top_10_schools = district_stats.head(10)
        fig_schools = px.bar(
            top_10_schools,
            x='Total Schools',
            y='District',
            orientation='h',
            color='Total Schools',
            color_continuous_scale='viridis'
        )
        fig_schools.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_schools, use_container_width=True)
    
    with chart_col4:
        st.subheader("Top 10 Districts by Trees Planted")
        top_10_trees = district_stats.sort_values('Trees Planted', ascending=False).head(10)
        fig_trees = px.bar(
            top_10_trees,
            x='Trees Planted',
            y='District',
            orientation='h',
            color='Trees Planted',
            color_continuous_scale='greens'
        )
        fig_trees.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_trees, use_container_width=True)

# School Management breakdown
st.subheader("🏫 School Management Distribution")

# Notification Distribution
st.markdown("#### 📢 Notification Upload Distribution")
notif_mgmt_stats = filtered_df.groupby('School Management').agg({
    'UDISE Code': 'count',
    'Notification Uploaded': lambda x: (x == 'Yes').sum()
}).reset_index()

notif_mgmt_stats.columns = ['School Management', 'Total Schools', 'Notifications Uploaded']
notif_mgmt_stats['Notification %'] = (notif_mgmt_stats['Notifications Uploaded'] / 
                                       notif_mgmt_stats['Total Schools'] * 100).round(2)

col_notif1, col_notif2 = st.columns([1, 2])

with col_notif1:
    st.dataframe(
        notif_mgmt_stats.style.format({
            'Total Schools': '{:,}',
            'Notifications Uploaded': '{:,}',
            'Notification %': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )

with col_notif2:
    fig_notif_mgmt = go.Figure()
    fig_notif_mgmt.add_trace(go.Bar(
        name='Total Schools', 
        x=notif_mgmt_stats['School Management'], 
        y=notif_mgmt_stats['Total Schools'], 
        marker_color='lightblue'
    ))
    fig_notif_mgmt.add_trace(go.Bar(
        name='Notifications Uploaded', 
        x=notif_mgmt_stats['School Management'], 
        y=notif_mgmt_stats['Notifications Uploaded'], 
        marker_color='lightgreen'
    ))
    fig_notif_mgmt.update_layout(barmode='group', height=300, title='Notification Status by Management')
    st.plotly_chart(fig_notif_mgmt, use_container_width=True)

st.markdown("---")

# Tree Distribution
st.markdown("#### 🌳 Tree Plantation Distribution")
tree_mgmt_stats = filtered_df.groupby('School Management').agg({
    'UDISE Code': 'count',
    'Trees Planted': 'sum',
    'Tree Uploaded': lambda x: (x == 'Yes').sum()
}).reset_index()

tree_mgmt_stats.columns = ['School Management', 'Total Schools', 'Trees Planted', 'Tree Data Uploaded']
tree_mgmt_stats['Tree Upload %'] = (tree_mgmt_stats['Tree Data Uploaded'] / 
                                     tree_mgmt_stats['Total Schools'] * 100).round(2)

col_tree1, col_tree2 = st.columns([1, 2])

with col_tree1:
    st.dataframe(
        tree_mgmt_stats.style.format({
            'Total Schools': '{:,}',
            'Trees Planted': '{:,}',
            'Tree Data Uploaded': '{:,}',
            'Tree Upload %': '{:.2f}%'
        }),
        hide_index=True,
        use_container_width=True
    )

with col_tree2:
    fig_tree_mgmt = go.Figure()
    fig_tree_mgmt.add_trace(go.Bar(
        name='Total Schools', 
        x=tree_mgmt_stats['School Management'], 
        y=tree_mgmt_stats['Total Schools'], 
        marker_color='lightblue'
    ))
    fig_tree_mgmt.add_trace(go.Bar(
        name='Tree Data Uploaded', 
        x=tree_mgmt_stats['School Management'], 
        y=tree_mgmt_stats['Tree Data Uploaded'], 
        marker_color='lightcoral'
    ))
    fig_tree_mgmt.update_layout(barmode='group', height=300, title='Tree Plantation Status by Management')
    st.plotly_chart(fig_tree_mgmt, use_container_width=True)

st.markdown("---")

# Data table
st.header("📋 School Details")
st.markdown(f"Showing **{len(filtered_df):,}** schools")

# Display options
show_all = st.checkbox("Show all records", value=False)
if show_all:
    display_df = filtered_df
else:
    display_df = filtered_df.head(100)
    st.info(f"Displaying first 100 records out of {len(filtered_df):,}. Check 'Show all records' to see all.")

# Format and display
st.dataframe(
    display_df.style.format({
        'Trees Planted': '{:,}'
    }),
    use_container_width=True,
    height=400
)

# Download button
st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name=f"eco_club_data_{selected_district.replace(' ', '_')}.csv",
    mime="text/csv"
)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; padding: 10px;'>
    Eco Club Dashboard - Uttar Pradesh | Data Service Module v1.0
    </div>
    """,
    unsafe_allow_html=True
)
