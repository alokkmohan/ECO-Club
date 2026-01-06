"""
FULLY AUTOMATED Eco Club Downloader
- Auto login
- Auto download both files
- Auto git push
- Can be scheduled to run every hour
"""

import os
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

# Configuration
WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")
WORKSPACE_FOLDER = r"d:\Eco club"

def load_credentials():
    """Load credentials from .env file"""
    env_file = Path(WORKSPACE_FOLDER) / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    userid = os.getenv('ECO_USERID')
    password = os.getenv('ECO_PASSWORD')
    
    if not userid or not password:
        print("❌ Error: Credentials not found in .env file!")
        return None, None
    
    return userid, password

def setup_driver():
    """Setup Chrome with headless mode for automation"""
    chrome_options = Options()
    
    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Run headless (without showing browser window)
    # Comment out these lines if you want to see the browser
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def wait_for_download(filename, timeout=90):
    """Wait for file to complete downloading"""
    file_path = Path(DOWNLOAD_FOLDER) / filename
    
    for i in range(timeout):
        if file_path.exists():
            time.sleep(2)
            return True
        time.sleep(1)
    
    return False

def delete_old_files():
    """Delete old Excel files from Downloads folder"""
    files = [
        Path(DOWNLOAD_FOLDER) / "UTTAR PRADESH.xlsx",
        Path(DOWNLOAD_FOLDER) / "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    for file in files:
        if file.exists():
            file.unlink()
            print(f"  🗑️  Deleted old: {file.name}")

def move_files_to_workspace():
    """Move downloaded files to workspace"""
    files = [
        "UTTAR PRADESH.xlsx",
        "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    moved_count = 0
    for filename in files:
        source = Path(DOWNLOAD_FOLDER) / filename
        destination = Path(WORKSPACE_FOLDER) / filename
        
        if source.exists():
            shutil.move(str(source), str(destination))
            print(f"  ✅ Moved: {filename}")
            moved_count += 1
        else:
            print(f"  ❌ Not found: {filename}")
    
    return moved_count

def push_to_git():
    """Push changes to git repository"""
    try:
        os.chdir(WORKSPACE_FOLDER)
        
        # Check if there are changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("  ℹ️  No changes to commit")
            return True
        
        # Add files
        subprocess.run(['git', 'add', 'UTTAR PRADESH.xlsx', 
                       'All_Schools_with_Notifications_UTTAR PRADESH.xlsx'],
                      check=True)
        
        # Commit
        commit_msg = f"Auto-update Eco Club data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        print(f"  ✅ Git push successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ Git error: {e}")
        return False

def main():
    start_time = datetime.now()
    print("=" * 70)
    print(f"🤖 AUTOMATED ECO CLUB DATA SYNC - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Load credentials
    print("\n[1] Loading credentials...")
    userid, password = load_credentials()
    if not userid:
        return
    print("  ✅ Credentials loaded")
    
    # Delete old files
    print("\n[2] Cleaning old downloads...")
    delete_old_files()
    
    # Setup browser
    print("\n[3] Starting browser...")
    driver = setup_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        # Open website
        print(f"\n[4] Opening {WEBSITE_URL}...")
        driver.get(WEBSITE_URL)
        time.sleep(3)
        print("  ✅ Page loaded")
        
        # Login
        print("\n[5] Logging in...")
        try:
            # Click Login button
            login_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Login') or contains(@class, 'adminLogin')]")
            ))
            login_btn.click()
            time.sleep(2)
            
            # Enter credentials
            userid_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@type='text' or @type='email' or @name='userid' or @id='userid']")
            ))
            userid_field.send_keys(userid)
            
            password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            password_field.send_keys(password)
            
            # Submit
            submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            time.sleep(5)
            
            print("  ✅ Login successful")
        except Exception as e:
            print(f"  ❌ Login failed: {e}")
            return
        
        # Download File 1
        print("\n[6] Downloading UTTAR PRADESH.xlsx...")
        try:
            download_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Download State Wise Data Excel')]")
            ))
            download_btn.click()
            
            if wait_for_download("UTTAR PRADESH.xlsx"):
                print("  ✅ Downloaded successfully")
            else:
                print("  ❌ Download timeout")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        time.sleep(3)
        
        # Download File 2
        print("\n[7] Downloading All_Schools_with_Notifications_UTTAR PRADESH.xlsx...")
        try:
            # Click on notification element (could be bell icon/card)
            notification_elem = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(), 'Total Notification')]")
            ))
            notification_elem.click()
            time.sleep(3)
            
            # Click download button
            download_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Download All Schools Excel')]")
            ))
            download_btn.click()
            
            if wait_for_download("All_Schools_with_Notifications_UTTAR PRADESH.xlsx"):
                print("  ✅ Downloaded successfully")
            else:
                print("  ❌ Download timeout")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
    finally:
        driver.quit()
        print("\n[8] Browser closed")
    
    # Move files
    print("\n[9] Moving files to workspace...")
    moved = move_files_to_workspace()
    
    # Push to git
    if moved > 0:
        print("\n[10] Pushing to Git...")
        push_to_git()
    else:
        print("\n[10] Skipping Git push (no files downloaded)")
    
    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 70)
    print(f"✅ PROCESS COMPLETE - Duration: {duration:.1f} seconds")
    print("=" * 70)

if __name__ == "__main__":
    main()
