"""
FINAL COMPLETE AUTOMATION
Sequence:
1. Login (manual first time, then session saved)
2. Click "DOWNLOAD STATE WISE DATA EXCEL" → UTTAR PRADESH.xlsx
3. Click "TOTAL NOTIFICATIONS UPLOADED" card → page change
4. Click "DOWNLOAD ALL SCHOOLS EXCEL" → All_Schools_with_Notifications_UTTAR PRADESH.xlsx
5. Move files to workspace
6. Git push
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
CHROME_PROFILE = r"d:\Eco club\chrome_profile"
LOG_FILE = Path(WORKSPACE_FOLDER) / "logs" / f"sync_{datetime.now().strftime('%Y%m%d')}.log"

def log(message):
    """Log to file and print"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    
    # Create logs folder if needed
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def setup_driver():
    """Setup Chrome with saved profile"""
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE}")
    
    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Comment out for headless mode (background)
    # chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_download(filename, timeout=90):
    """Wait for file to complete downloading"""
    file_path = Path(DOWNLOAD_FOLDER) / filename
    
    log(f"  Waiting for {filename}...")
    for i in range(timeout):
        if file_path.exists():
            time.sleep(2)  # Ensure complete
            log(f"  ✅ {filename} downloaded")
            return True
        time.sleep(1)
    
    log(f"  ❌ {filename} timeout")
    return False

def delete_old_files():
    """Delete old Excel files from Downloads"""
    files = [
        "UTTAR PRADESH.xlsx",
        "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    for filename in files:
        file_path = Path(DOWNLOAD_FOLDER) / filename
        if file_path.exists():
            file_path.unlink()
            log(f"  Deleted old: {filename}")

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
            log(f"  ✅ Moved: {filename}")
            moved += 1
        else:
            log(f"  ❌ Not found: {filename}")
    
    return moved

def push_to_git():
    """Push changes to git repository"""
    try:
        os.chdir(WORKSPACE_FOLDER)
        
        # Check if there are changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            log("  No changes to commit")
            return True
        
        # Add files
        subprocess.run(['git', 'add', 'UTTAR PRADESH.xlsx', 
                       'All_Schools_with_Notifications_UTTAR PRADESH.xlsx'],
                      check=True)
        
        # Commit
        commit_msg = f"Auto-update - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # Push
        subprocess.run(['git', 'push'], check=True)
        
        log("  ✅ Git push successful")
        return True
        
    except Exception as e:
        log(f"  ❌ Git error: {e}")
        return False

def main():
    start_time = datetime.now()
    log("=" * 70)
    log("ECO CLUB AUTO SYNC STARTED")
    log("=" * 70)
    
    # Check if first run
    first_run = not Path(CHROME_PROFILE).exists()
    
    if first_run:
        log("\n⚠️  FIRST TIME SETUP - Manual login required")
    
    # Delete old files
    log("\n[1] Cleaning old downloads...")
    delete_old_files()
    
    # Setup browser
    log("\n[2] Starting browser...")
    driver = setup_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        # Open website
        log(f"\n[3] Opening {WEBSITE_URL}...")
        driver.get(WEBSITE_URL)
        time.sleep(3)
        
        if first_run:
            log("\n👉 Please LOGIN now in the browser")
            log("   After login, press ENTER here...")
            input()
            log("  ✅ Session saved for future!")
        else:
            log("  ✅ Using saved session")
        
        # STEP 1: Download UTTAR PRADESH.xlsx
        log("\n[4] Step 1: Downloading UTTAR PRADESH.xlsx...")
        try:
            # Try multiple button text variations
            btn = None
            button_variations = [
                "DOWNLOAD STATE WISE DATA EXCEL",
                "Download State Wise Data Excel",
                "Download State wise data excel",
            ]
            
            for btn_text in button_variations:
                try:
                    btn = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//button[contains(text(), '{btn_text}')]")
                    ))
                    log(f"  ✅ Found button: '{btn_text}'")
                    break
                except:
                    continue
            
            # If still not found, try by class
            if not btn:
                try:
                    btn = driver.find_element(By.XPATH, 
                        "//button[contains(@class, 'btn-primary') and contains(., 'Download') and contains(., 'State')]")
                    log("  ✅ Found button by class")
                except:
                    pass
            
            if btn:
                btn.click()
                log("  ✅ Clicked download button")
                wait_for_download("UTTAR PRADESH.xlsx")
            else:
                log("  ❌ Download button not found")
            
        except Exception as e:
            log(f"  ❌ Error: {e}")
        
        time.sleep(3)
        
        # STEP 2: Click notification card
        log("\n[5] Step 2: Clicking notification card...")
        try:
            card = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class, 'boxdivThree')]")
            ))
            card.click()
            log("  ✅ Card clicked, waiting for page change...")
            time.sleep(5)  # Wait for page to load
            
        except Exception as e:
            log(f"  ❌ Error clicking card: {e}")
        
        # STEP 3: Download All Schools Excel
        log("\n[6] Step 3: Downloading notifications file...")
        try:
            # Try multiple button texts
            btn = None
            button_texts = [
                "DOWNLOAD ALL SCHOOLS EXCEL",
                "Download All Schools Excel",
                "DOWNLOAD EXCEL",
                "Download Excel"
            ]
            
            for btn_text in button_texts:
                try:
                    btn = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, f"//button[contains(text(), '{btn_text}')]")
                    ))
                    log(f"  ✅ Found button: '{btn_text}'")
                    break
                except:
                    continue
            
            if btn:
                btn.click()
                log("  ✅ Clicked download button")
                wait_for_download("All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
            else:
                log("  ❌ Download button not found")
                
        except Exception as e:
            log(f"  ❌ Error: {e}")
        
    except Exception as e:
        log(f"\n❌ Unexpected error: {e}")
    finally:
        driver.quit()
        log("\n[7] Browser closed")
    
    # Move files
    log("\n[8] Moving files to workspace...")
    moved = move_files_to_workspace()
    
    # Push to git
    if moved > 0:
        log("\n[9] Pushing to Git...")
        push_to_git()
    else:
        log("\n[9] Skipping Git push (no files downloaded)")
    
    # Summary
    duration = (datetime.now() - start_time).total_seconds()
    log("\n" + "=" * 70)
    log(f"✅ SYNC COMPLETE - Duration: {duration:.1f}s")
    log(f"   Files downloaded: {moved}/2")
    log("=" * 70)
    
    if first_run:
        log("\n💡 Session saved! Future runs will be fully automatic.")

if __name__ == "__main__":
    main()
