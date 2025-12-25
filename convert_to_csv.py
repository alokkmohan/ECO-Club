"""
Convert Excel files to CSV for faster loading
Run this once when data updates
"""
import pandas as pd
from pathlib import Path

print("Converting Excel files to CSV...")

# School Master
print("1. Converting School Master.xlsx...")
df = pd.read_excel("School Master.xlsx", dtype=str)
df.to_csv("School Master.csv", index=False)
print(f"   ✓ Created School Master.csv ({len(df)} rows)")

# Notifications
print("2. Converting All_Schools_with_Notifications_UTTAR PRADESH.xlsx...")
df = pd.read_excel("All_Schools_with_Notifications_UTTAR PRADESH.xlsx", dtype=str)
df.to_csv("Notifications.csv", index=False)
print(f"   ✓ Created Notifications.csv ({len(df)} rows)")

# Tree Data
print("3. Converting UTTAR PRADESH.xlsx...")
df = pd.read_excel("UTTAR PRADESH.xlsx", dtype=str)
df.to_csv("Tree_Data.csv", index=False)
print(f"   ✓ Created Tree_Data.csv ({len(df)} rows)")

print("\n✅ All files converted! Dashboard will now load much faster.")
print("Note: Run this script again whenever you update the Excel files.")
