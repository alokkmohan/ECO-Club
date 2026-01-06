"""
Session-Based Automation
Login once, then session is saved forever!
No need to login again
"""

import time
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")
WORKSPACE_FOLDER = r"d:\Eco club"
CHROME_PROFILE = r"d:\Eco club\chrome_profile"  # Saved session location

def setup_driver_with_profile():
    """Setup Chrome with saved profile to maintain session"""
    chrome_options = Options()
    
    # Use saved profile
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE}")
    
    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Headless mode for automation (comment out these 3 lines to see browser)
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_download(filename, timeout=90):
    """Wait for file to complete downloading"""
    file_path = Path(DOWNLOAD_FOLDER) / filename
    
    print(f"    Waiting for {filename}...", end='', flush=True)
    for i in range(timeout):
        if file_path.exists():
            time.sleep(2)
            print(" ✅")
            return True
        print(".", end='', flush=True)
        time.sleep(1)
    
    print(" ❌ Timeout!")
    return False

def delete_old_files():
    """Delete old Excel files from Downloads"""
    files = [
        Path(DOWNLOAD_FOLDER) / "UTTAR PRADESH.xlsx",
        Path(DOWNLOAD_FOLDER) / "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    for file in files:
        if file.exists():
            file.unlink()

def move_files_to_workspace():
    """Move downloaded files to workspace"""
    files = [
        "UTTAR PRADESH.xlsx",
        "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    moved = 0
    for filename in files:
        source = Path(DOWNLOAD_FOLDER) / filename
        destination = Path(WORKSPACE_FOLDER) / filename
        
        if source.exists():
            shutil.move(str(source), str(destination))
            print(f"  ✅ Moved: {filename}")
            moved += 1
        else:
            print(f"  ❌ Not found: {filename}")
    
    return moved

def push_to_git():
    """Push changes to git"""
    try:
        import os
        os.chdir(WORKSPACE_FOLDER)
        
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("  ℹ️  No changes to commit")
            return True
        
        subprocess.run(['git', 'add', 'UTTAR PRADESH.xlsx', 
                       'All_Schools_with_Notifications_UTTAR PRADESH.xlsx'],
                      check=True)
        
        commit_msg = f"Auto-update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print(f"  ✅ Git push successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ Git error: {e}")
        return False

def main():
    start_time = datetime.now()
    print("=" * 70)
    print(f"🤖 SESSION-BASED AUTO SYNC - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Check if this is first run
    first_run = not Path(CHROME_PROFILE).exists()
    
    if first_run:
        print("\n⚠️  FIRST TIME SETUP")
        print("=" * 70)
        print("Browser will open. Please LOGIN manually.")
        print("After login, come back here and press ENTER to continue...")
        print("=" * 70)
    
    print("\n[1] Cleaning old downloads...")
    delete_old_files()
    
    print("\n[2] Starting browser with saved session...")
    driver = setup_driver_with_profile()
    wait = WebDriverWait(driver, 30)
    
    try:
        print(f"\n[3] Opening {WEBSITE_URL}...")
        driver.get(WEBSITE_URL)
        time.sleep(3)
        
        if first_run:
            print("\n👉 Please LOGIN now in the browser window...")
            print("After successful login, press ENTER here...")
            input()
            print("  ✅ Session will be saved!")
        else:
            print("  ✅ Using saved session")
        
        # Download File 1
        print("\n[4] Downloading UTTAR PRADESH.xlsx...")
        try:
            btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Download State Wise Data Excel')]")
            ))
            btn.click()
            
            if wait_for_download("UTTAR PRADESH.xlsx"):
                print("  ✅ File 1 downloaded")
            else:
                print("  ❌ File 1 failed")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(3)
        
        # Download File 2
        print("\n[5] Downloading notifications file...")
        try:
            # Click on the card/div with "TOTAL NOTIFICATIONS UPLOADED"
            # This is a clickable card, not a button
            notification_card = None
            
            # Try finding by class (boxdivThree seems to be the notification card)
            try:
                notification_card = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class, 'boxdivThree')]")
                ))
                print("  ✅ Found notification card by class")
            except:
                # Try finding by text
                try:
                    notification_card = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//div[contains(text(), 'TOTAL') and contains(text(), 'NOTIFICATIONS UPLOADED')]")
                    ))
                    print("  ✅ Found notification card by text")
                except:
                    print("  ❌ Notification card not found")
            
            if notification_card:
                notification_card.click()
                print("  ✅ Clicked notification card")
                time.sleep(3)
                
                # Now look for download button
                btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'DOWNLOAD') and contains(text(), 'EXCEL')]")
                ))
                btn.click()
                print("  ✅ Clicked download button")
                
                if wait_for_download("All_Schools_with_Notifications_UTTAR PRADESH.xlsx"):
                    print("  ✅ File 2 downloaded")
                else:
                    print("  ❌ File 2 download timeout")
            else:
                print("  ❌ Could not find notification card")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
    finally:
        driver.quit()
        print("\n[6] Browser closed")
    
    # Move files
    print("\n[7] Moving files to workspace...")
    moved = move_files_to_workspace()
    
    # Push to git
    if moved > 0:
        print("\n[8] Pushing to Git...")
        push_to_git()
    else:
        print("\n[8] Skipping Git push (no files)")
    
    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 70)
    print(f"✅ COMPLETE - Duration: {duration:.1f}s")
    print("=" * 70)
    
    if first_run:
        print("\n💡 Session saved! Next time no login needed.")
        print("   You can now schedule this to run automatically!")

if __name__ == "__main__":
    main()
