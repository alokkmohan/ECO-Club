"""
Update notification data by merging master table with notification uploads
"""

import pandas as pd

def update_notification_data():
    """Merge master table with notification uploads and generate complete data."""
    
    print("Loading master table...")
    df_master = pd.read_csv('School Master.csv')
    print(f"Master table: {len(df_master)} schools")
    
    print("\nLoading notification uploads...")
    df_notif = pd.read_excel('All_Schools_with_Notifications_UTTAR PRADESH.xlsx')
    print(f"Notification uploads: {len(df_notif)} schools")
    
    # Rename columns in notification file to match
    df_notif = df_notif.rename(columns={
        'UDISE ID': 'UDISE Code',
        'District': 'District Name'
    })
    
    # Convert UDISE Code to string with leading zeros (11 digits)
    df_notif['UDISE Code'] = df_notif['UDISE Code'].astype(str).str.zfill(11)
    df_master['UDISE Code'] = df_master['UDISE Code'].astype(str).str.zfill(11)
    
    # Add a marker column for schools that uploaded notification
    df_notif['Notification Uploaded'] = 'Yes'
    
    # Merge with master table
    df_merged = df_master.merge(
        df_notif[['UDISE Code', 'Notification Uploaded']],
        on='UDISE Code',
        how='left'
    )
    
    # Fill NaN with 'No' for schools that didn't upload
    df_merged['Notification Uploaded'] = df_merged['Notification Uploaded'].fillna('No')
    
    # Add Tree columns (default to No/0)
    df_merged['Tree Uploaded'] = 'No'
    df_merged['Trees Planted'] = 0
    
    # Rename District Name to District for consistency
    df_merged = df_merged.rename(columns={'District Name': 'District'})
    
    # Save updated data
    output_file = 'Updated_School_Data.csv'
    df_merged.to_csv(output_file, index=False)
    print(f"\n✓ Updated data saved to: {output_file}")
    print(f"  Total schools: {len(df_merged)}")
    print(f"  Notification uploaded: {len(df_merged[df_merged['Notification Uploaded'] == 'Yes'])}")
    print(f"  Notification NOT uploaded: {len(df_merged[df_merged['Notification Uploaded'] == 'No'])}")
    
    return df_merged

if __name__ == "__main__":
    update_notification_data()
