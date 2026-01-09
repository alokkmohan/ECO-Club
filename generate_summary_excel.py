"""
Auto-generate Eco-Club-Complete_Summary.xlsx from source data
This ensures summary Excel is always up-to-date with latest source data
"""

import pandas as pd
from datetime import datetime

def generate_summary_excel(source_file='All_Schools_with_Notifications_UTTAR PRADESH.xlsx', 
                           output_file='Eco-Club-Complete_Summary.xlsx'):
    """Generate complete summary Excel from source data."""
    
    print(f"Loading source data: {source_file}")
    
    try:
        # Read source data
        df_all = pd.read_excel(source_file)
        print(f"Loaded {len(df_all)} school records")
        
        # Generate district-wise summary
        district_summary = df_all.groupby('District').agg({
            'School Name': 'count',
            'Notification Uploaded': lambda x: (x == 'Yes').sum()
        }).reset_index()
        
        district_summary.columns = ['District', 'Total Schools', 'Eco-Club Notification Uploaded']
        district_summary['Percentage (%)'] = (
            district_summary['Eco-Club Notification Uploaded'] / 
            district_summary['Total Schools'] * 100
        ).round(2)
        
        # Sort by percentage descending
        district_summary_sorted = district_summary.sort_values('Percentage (%)', ascending=False).reset_index(drop=True)
        
        print(f"Generated summary for {len(district_summary)} districts")
        
        # Top 10 and Bottom 25
        top_10 = district_summary_sorted.head(10).copy()
        bottom_25 = district_summary_sorted.tail(25).copy()
        
        # Calculate overall statistics
        total_districts = len(district_summary)
        total_schools = district_summary['Total Schools'].sum()
        total_notified = district_summary['Eco-Club Notification Uploaded'].sum()
        avg_pct = (total_notified / total_schools * 100) if total_schools > 0 else 0
        
        # Categorize districts
        excellent = len(district_summary[district_summary['Percentage (%)'] >= 75])
        good = len(district_summary[(district_summary['Percentage (%)'] >= 50) & (district_summary['Percentage (%)'] < 75)])
        average = len(district_summary[(district_summary['Percentage (%)'] >= 25) & (district_summary['Percentage (%)'] < 50)])
        critical = len(district_summary[district_summary['Percentage (%)'] < 25])
        
        # Create Overall Summary
        overall_summary = pd.DataFrame({
            'Metric': [
                'Total Districts',
                'Total Schools',
                'Total Notifications Uploaded',
                'Average Completion %',
                'Districts with ≥75%',
                'Districts with 50-75%',
                'Districts with 25-50%',
                'Districts with <25%'
            ],
            'Value': [
                total_districts,
                total_schools,
                total_notified,
                f'{avg_pct:.2f}%',
                excellent,
                good,
                average,
                critical
            ]
        })
        
        # Write to Excel with multiple sheets
        print(f"Creating Excel file: {output_file}")
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            district_summary_sorted.to_excel(writer, sheet_name='All Districts', index=False)
            top_10.to_excel(writer, sheet_name='Top 10', index=False)
            bottom_25.to_excel(writer, sheet_name='Bottom 25', index=False)
            overall_summary.to_excel(writer, sheet_name='Overall Summary', index=False)
        
        print(f"✓ Summary Excel created successfully!")
        print(f"  - All Districts: {len(district_summary_sorted)} rows")
        print(f"  - Top 10: {len(top_10)} rows")
        print(f"  - Bottom 25: {len(bottom_25)} rows")
        print(f"  - Overall Summary: {len(overall_summary)} rows")
        print(f"  - Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error generating summary: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    generate_summary_excel()
