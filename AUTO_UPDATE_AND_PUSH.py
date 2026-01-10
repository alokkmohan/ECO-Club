"""
🚀 AUTOMATIC DATA UPDATE AND GIT PUSH SCRIPT
================================================
This script automatically:
1. Merges notification and tree data with master table
2. Generates summary Excel report
3. Commits and pushes to GitHub
4. Updates Streamlit Cloud dashboard

Just replace these 2 files in the folder and run this script:
- All_Schools_with_Notifications_UTTAR PRADESH.xlsx
- UTTAR PRADESH.xlsx
"""

import pandas as pd
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def print_step(step_num, message):
    """Print formatted step message."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {message}")
    print(f"{'='*60}")

def update_complete_data():
    """Merge master table with notification uploads and tree data."""
    
    print_step(1, "LOADING AND MERGING DATA")
    
    print("📂 Loading master table...")
    df_master = pd.read_csv('School Master.csv', dtype=str)
    print(f"   ✓ Master table: {len(df_master)} schools")
    
    # Normalize UDISE codes
    df_master['UDISE Code'] = df_master['UDISE Code'].astype(str).str.strip().str.replace('.0', '', regex=False).str.replace(r'\D', '', regex=True).str.zfill(11)
    
    # Rename District Name to District
    if 'District Name' in df_master.columns:
        df_master = df_master.rename(columns={'District Name': 'District'})
    
    # Load and merge notification data
    print("\n📧 Loading notification uploads...")
    df_notif = pd.read_excel('All_Schools_with_Notifications_UTTAR PRADESH.xlsx', dtype=str)
    print(f"   ✓ Notification uploads: {len(df_notif)} records")
    
    # Find UDISE column in notification file
    notif_udise_col = [col for col in df_notif.columns if 'UDISE' in str(col).upper()][0]
    
    # Normalize UDISE codes in notification file
    df_notif[notif_udise_col] = df_notif[notif_udise_col].astype(str).str.strip().str.replace('.0', '', regex=False).str.replace(r'\D', '', regex=True).str.zfill(11)
    
    # Add Notification Uploaded column
    df_notif['Notification Uploaded'] = 'Yes'
    
    # Merge with master table
    df_merged = df_master.merge(
        df_notif[[notif_udise_col, 'Notification Uploaded']].rename(columns={notif_udise_col: 'UDISE Code'}),
        on='UDISE Code',
        how='left'
    )
    
    # Fill NaN with 'No' for schools that didn't upload notification
    df_merged['Notification Uploaded'] = df_merged['Notification Uploaded'].fillna('No')
    
    # Load and merge tree data
    print("\n🌳 Loading tree plantation data...")
    df_tree = pd.read_csv('Tree_Data.csv', dtype=str)
    print(f"   ✓ Tree data: {len(df_tree)} records")
    
    # Normalize UDISE codes in tree file
    df_tree['UDISE ID'] = df_tree['UDISE ID'].astype(str).str.strip().str.replace('.0', '', regex=False).str.replace(r'\D', '', regex=True).str.zfill(11)
    
    # Convert Saplings to numeric
    df_tree['Saplings'] = pd.to_numeric(df_tree['Saplings'], errors='coerce').fillna(0).astype(int)
    
    # Aggregate tree data by UDISE Code (sum all saplings per school)
    tree_agg = df_tree.groupby('UDISE ID')['Saplings'].sum().reset_index()
    tree_agg.columns = ['UDISE Code', 'Trees Planted']
    
    # Add Tree Uploaded marker
    tree_agg['Tree Uploaded'] = 'Yes'
    
    # Merge tree data with main dataframe
    df_merged = df_merged.merge(
        tree_agg,
        on='UDISE Code',
        how='left'
    )
    
    # Fill NaN values for schools without tree data
    df_merged['Tree Uploaded'] = df_merged['Tree Uploaded'].fillna('No')
    df_merged['Trees Planted'] = df_merged['Trees Planted'].fillna(0).astype(int)
    
    # Save updated data
    output_file = 'Updated_School_Data.csv'
    df_merged.to_csv(output_file, index=False)
    
    # Calculate summary
    total_schools = len(df_merged)
    notif_yes = len(df_merged[df_merged['Notification Uploaded'] == 'Yes'])
    notif_no = len(df_merged[df_merged['Notification Uploaded'] == 'No'])
    tree_yes = len(df_merged[df_merged['Tree Uploaded'] == 'Yes'])
    tree_no = len(df_merged[df_merged['Tree Uploaded'] == 'No'])
    total_trees = df_merged['Trees Planted'].sum()
    
    print(f"\n✅ Updated data saved to: {output_file}")
    print(f"\n📊 DATA SUMMARY:")
    print(f"   • Total schools: {total_schools:,}")
    print(f"   • Notification uploaded: {notif_yes:,}")
    print(f"   • Notification NOT uploaded: {notif_no:,}")
    print(f"   • Tree uploaded: {tree_yes:,}")
    print(f"   • Tree NOT uploaded: {tree_no:,}")
    print(f"   • Total trees planted: {total_trees:,}")
    
    return df_merged, notif_yes, tree_yes, total_trees

def generate_summary_excel(df):
    """Generate summary Excel file."""
    
    print_step(2, "GENERATING SUMMARY EXCEL REPORT")
    
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
    
    # Add TOTAL row
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
    
    # Top 10 and Bottom 25
    top_10 = district_summary.nlargest(10, 'Percentage (%)')
    bottom_25 = district_summary.nsmallest(25, 'Percentage (%)')
    
    # Calculate tree totals
    total_schools = total_row['Total Schools'].iloc[0]
    total_notif_uploaded = total_row['Eco-Club Notification Uploaded'].iloc[0]
    notif_percentage = total_row['Percentage (%)'].iloc[0]
    
    total_tree_uploaded = len(df[df['Tree Uploaded'] == 'Yes'])
    total_trees_planted = df['Trees Planted'].sum()
    tree_percentage = (total_tree_uploaded / total_schools * 100).round(2) if total_schools > 0 else 0
    
    # Save to Excel
    summary_xlsx = 'Eco-Club-Complete_Summary.xlsx'
    with pd.ExcelWriter(summary_xlsx, engine='openpyxl') as writer:
        # All Districts
        district_summary_with_total.to_excel(writer, sheet_name='All Districts', index=False)
        # Top 10
        top_10.to_excel(writer, sheet_name='Top 10', index=False)
        # Bottom 25
        bottom_25.to_excel(writer, sheet_name='Bottom 25', index=False)
        # Overall Summary
        summary_sheet = pd.DataFrame({
            'Metric': [
                'Total Schools', 
                'Total Notifications Uploaded', 
                'Notification Percentage (%)',
                'Total Tree Uploaded',
                'Total Trees Planted',
                'Tree Upload Percentage (%)'
            ],
            'Value': [
                total_schools,
                total_notif_uploaded,
                notif_percentage,
                total_tree_uploaded,
                total_trees_planted,
                tree_percentage
            ]
        })
        summary_sheet.to_excel(writer, sheet_name='Overall Summary', index=False)
    
    print(f"   ✅ Summary Excel saved: {summary_xlsx}")

def git_push(notif_count, tree_count, total_trees):
    """Commit and push to GitHub."""
    
    print_step(3, "COMMITTING AND PUSHING TO GITHUB")
    
    try:
        # Add all changes
        print("   📝 Adding files to git...")
        subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
        
        # Create commit message with current date and stats
        commit_msg = f"Auto-update {datetime.now().strftime('%Y-%m-%d')}: {notif_count:,} notifications, {tree_count:,} tree uploads, {total_trees:,} trees planted"
        
        print(f"   💬 Creating commit: {commit_msg}")
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, capture_output=True)
        
        # Push to GitHub
        print("   🚀 Pushing to GitHub...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], check=True, capture_output=True, text=True)
        
        print("   ✅ Successfully pushed to GitHub!")
        print("\n   🌐 Streamlit Cloud will auto-deploy in 2-3 minutes")
        print("   🔗 Dashboard: https://ecoclubup.streamlit.app/")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git error: {e}")
        print(f"   Output: {e.output if hasattr(e, 'output') else 'No output'}")
        return False

def main():
    """Main execution function."""
    
    print("\n" + "🚀"*30)
    print(" "*10 + "ECO CLUB AUTO UPDATE & PUSH")
    print("🚀"*30 + "\n")
    
    try:
        # Step 1: Update data
        df, notif_count, tree_count, total_trees = update_complete_data()
        
        # Step 2: Generate summary
        generate_summary_excel(df)
        
        # Step 3: Git push
        success = git_push(notif_count, tree_count, total_trees)
        
        if success:
            print("\n" + "✅"*30)
            print(" "*10 + "ALL STEPS COMPLETED SUCCESSFULLY!")
            print("✅"*30 + "\n")
            print("📊 Summary:")
            print(f"   • Notifications: {notif_count:,}")
            print(f"   • Tree Uploads: {tree_count:,}")
            print(f"   • Trees Planted: {total_trees:,}")
            print("\n🎉 Dashboard will update automatically in 2-3 minutes!")
        else:
            print("\n⚠️ Data updated locally but Git push failed.")
            print("Please check Git configuration and try again.")
            
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: Required file not found: {e}")
        print("\nMake sure these files exist in the folder:")
        print("   1. School Master.csv")
        print("   2. All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        print("   3. UTTAR PRADESH.xlsx (will be converted to Tree_Data.csv)")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
