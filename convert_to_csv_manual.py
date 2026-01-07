import pandas as pd

print("Converting Excel to CSV...")
print("-" * 50)

# Try reading the Excel file
try:
    df = pd.read_excel('All_Schools_with_Notifications_UTTAR PRADESH.xlsx', engine='openpyxl', dtype=str)
    print(f"✅ Excel loaded: {len(df)} rows, {len(df.columns)} columns")
    
    if len(df.columns) > 0:
        print(f"Columns: {df.columns.tolist()}")
        
    if len(df) > 0:
        print(f"\nFirst few rows:")
        print(df.head(3))
        
    # Save to CSV
    df.to_csv('Notifications.csv', index=False)
    print(f"\n✅ CSV created: Notifications.csv")
    
except Exception as e:
    print(f"❌ Error: {e}")
