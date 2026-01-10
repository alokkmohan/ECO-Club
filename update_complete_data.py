"""
Update complete school data by merging notification and tree data with master table
"""

import pandas as pd

def update_complete_data():
    """Merge master table with notification uploads and tree data."""
    
    print("Loading master table...")
    df_master = pd.read_csv('School Master.csv', dtype=str)
    print(f"Master table: {len(df_master)} schools")
    
    # Normalize UDISE codes
    df_master['UDISE Code'] = df_master['UDISE Code'].astype(str).str.strip().str.replace('.0', '', regex=False).str.replace(r'\D', '', regex=True).str.zfill(11)
    
    # Rename District Name to District
    if 'District Name' in df_master.columns:
        df_master = df_master.rename(columns={'District Name': 'District'})
    
    # Load and merge notification data
    print("\nLoading notification uploads...")
    df_notif = pd.read_excel('All_Schools_with_Notifications_UTTAR PRADESH.xlsx', dtype=str)
    print(f"Notification uploads: {len(df_notif)} schools")
    
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
    print("\nLoading tree plantation data...")
    df_tree = pd.read_csv('Tree_Data.csv', dtype=str)
    print(f"Tree data: {len(df_tree)} records")
    
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
    
    print(f"\n✓ Updated data saved to: {output_file}")
    print(f"\n📊 Summary:")
    print(f"  Total schools: {len(df_merged)}")
    print(f"  Notification uploaded: {len(df_merged[df_merged['Notification Uploaded'] == 'Yes'])}")
    print(f"  Notification NOT uploaded: {len(df_merged[df_merged['Notification Uploaded'] == 'No'])}")
    print(f"  Tree uploaded: {len(df_merged[df_merged['Tree Uploaded'] == 'Yes'])}")
    print(f"  Tree NOT uploaded: {len(df_merged[df_merged['Tree Uploaded'] == 'No'])}")
    print(f"  Total trees planted: {df_merged['Trees Planted'].sum():,}")
    
    return df_merged

if __name__ == "__main__":
    update_complete_data()
