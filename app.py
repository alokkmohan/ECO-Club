# Tab 3: Summary Report
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
                "�� Overall Notification Rate",
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
        

        

        
        # 1. District-wise Summary Report