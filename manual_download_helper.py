"""
Manual Download Helper - Browser stays open for you to download manually
"""

import time
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")
WORKSPACE_FOLDER = r"d:\Eco club"
CHROME_PROFILE = r"d:\Eco club\chrome_profile"

def main():
    print("=" * 70)
    print("MANUAL DOWNLOAD MODE")
    print("=" * 70)
    
    # Clean old files
    print("\nDeleting old files from Downloads...")
    for f in ["UTTAR PRADESH.xlsx", "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"]:
        fp = Path(DOWNLOAD_FOLDER) / f
        if fp.exists():
            fp.unlink()
            print(f"  Deleted: {f}")
    
    # Setup browser
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE}")
    prefs = {"download.default_directory": DOWNLOAD_FOLDER}
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    print(f"\nOpening {WEBSITE_URL}...")
    driver.get(WEBSITE_URL)
    time.sleep(3)
    
    print("\n" + "=" * 70)
    print("BROWSER IS OPEN - Download both files manually:")
    print("=" * 70)
    print("1. Click 'Download State Wise Data Excel' → UTTAR PRADESH")
    print("2. Click 'Total Notifications Uploaded' (bell icon)")
    print("3. Click 'Download All Schools Excel'")
    print("\nWhen both files are downloaded, press ENTER here...")
    print("=" * 70)
    
    input()
    
    driver.quit()
    print("\nBrowser closed.")
    
    # Move files
    print("\nMoving files to workspace...")
    moved = 0
    for filename in ["UTTAR PRADESH.xlsx", "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"]:
        source = Path(DOWNLOAD_FOLDER) / filename
        dest = Path(WORKSPACE_FOLDER) / filename
        
        if source.exists():
            shutil.move(str(source), str(dest))
            print(f"  ✅ {filename}")
            moved += 1
        else:
            print(f"  ❌ {filename} - Not found")
    
    if moved == 2:
        print("\n✅ Both files ready!")
        print("\nPush to Git? (y/n)")
        if input().lower() == 'y':
            import subprocess, os
            os.chdir(WORKSPACE_FOLDER)
            subprocess.run(['git', 'add', '*.xlsx'])
            subprocess.run(['git', 'commit', '-m', f'Manual update - {time.strftime("%Y-%m-%d %H:%M")}'])
            subprocess.run(['git', 'push'])
            print("✅ Pushed to Git!")
    else:
        print(f"\n⚠️  Only {moved}/2 files found")

if __name__ == "__main__":
    main()
