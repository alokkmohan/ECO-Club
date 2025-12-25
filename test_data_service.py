"""
Test script for DataService
"""
from data_service import DataService
import traceback

# Initialize the service
data_service = DataService(".")

# Load data
try:
    df, success, error = data_service.load_data()
except Exception as e:
    print(f"Exception during load: {e}")
    traceback.print_exc()
    success = False
    error = str(e)

if success:
    print("✓ Data loaded successfully!")
    print(f"\nTotal schools: {len(df)}")
    print(f"\nColumns: {list(df.columns)}")
    
    # Get districts
    districts = data_service.get_districts(df)
    print(f"\nNumber of districts: {len(districts)}")
    print(f"Districts: {districts[:5]}..." if len(districts) > 5 else f"Districts: {districts}")
    
    # Show summary statistics
    print(f"\n--- Summary ---")
    print(f"Notifications uploaded: {(df['Notification Uploaded'] == 'Yes').sum()}")
    print(f"Trees uploaded: {(df['Tree Uploaded'] == 'Yes').sum()}")
    print(f"Total trees planted: {df['Trees Planted'].sum()}")
    
    # Show first few rows
    print(f"\n--- First 5 schools ---")
    print(df.head())
else:
    print(f"✗ Error: {error}")
