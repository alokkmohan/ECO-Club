"""
Automated script to download Eco Club data files and upload to Git
Downloads:
1. UTTAR PRADESH.xlsx (State wise data)
2. All_Schools_with_Notifications_UTTAR PRADESH.xlsx (All schools with notifications)
"""

import os
import time
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
from datetime import datetime

# Configuration
WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")
WORKSPACE_FOLDER = r"d:\Eco club"

# Load credentials from environment variables or .env file
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
        print("Error: Credentials not found!")
        print("Please create .env file with:")
        print("ECO_USERID=your_userid")
        print("ECO_PASSWORD=your_password")
        exit(1)
    
    return userid, password

def setup_driver():
    """Setup Chrome browser with download preferences"""
    chrome_options = Options()
    
    # Set download directory
    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Uncomment to run headless (without browser window)
    # chrome_options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_download(filename, timeout=60):
    """Wait for a file to be downloaded"""
    file_path = Path(DOWNLOAD_FOLDER) / filename
    seconds = 0
    
    # Wait for file to appear
    while seconds < timeout:
        # Check for both the file and temporary download files
        if file_path.exists():
            # Wait a bit more to ensure download is complete
            time.sleep(2)
            return True
        
        # Check for partial download files
        partial_files = list(Path(DOWNLOAD_FOLDER).glob(f"{filename}.*"))
        if partial_files:
            time.sleep(1)
            seconds += 1
            continue
            
        time.sleep(1)
        seconds += 1
    
    return False

def download_files(userid, password):
    """Main function to download files from website"""
    print("Starting browser...")
    driver = setup_driver()
    
    try:
        # Navigate to website
        print(f"Opening website: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)
        
        # Wait for page to load
        wait = WebDriverWait(driver, 20)
        
        # Login
        print("Logging in...")
        userid_field = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        password_field = driver.find_element(By.ID, "password")
        
        userid_field.clear()
        userid_field.send_keys(userid)
        password_field.clear()
        password_field.send_keys(password)
        
        # Click login button
        login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_button.click()
        
        time.sleep(3)  # Wait for login to complete
        
        # Download File 1: UTTAR PRADESH.xlsx (State wise data)
        print("\nDownloading UTTAR PRADESH.xlsx...")
        try:
            # Look for "Download State Wise Data Excel" button (exact text from website)
            download_state_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download State Wise Data Excel')]"))
            )
            download_state_btn.click()
            
            if wait_for_download("UTTAR PRADESH.xlsx", timeout=30):
                print("✓ UTTAR PRADESH.xlsx downloaded successfully")
            else:
                print("✗ Failed to download UTTAR PRADESH.xlsx")
        except Exception as e:
            print(f"Error downloading state data: {e}")
        
        time.sleep(2)
        
        # Download File 2: All_Schools_with_Notifications_UTTAR PRADESH.xlsx
        print("\nDownloading All_Schools_with_Notifications_UTTAR PRADESH.xlsx...")
        try:
            # Click on "Download All Schools Excel" button (exact text from website)
            download_all_schools_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download All Schools Excel')]"))
            )
            download_all_schools_btn.click()
            
            if wait_for_download("All_Schools_with_Notifications_UTTAR PRADESH.xlsx", timeout=30):
                print("✓ All_Schools_with_Notifications_UTTAR PRADESH.xlsx downloaded successfully")
            else:
                print("✗ Failed to download All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        except Exception as e:
            print(f"Error downloading notifications data: {e}")
        
        time.sleep(2)
        print("\nDownload completed!")
        
    except Exception as e:
        print(f"Error during download: {e}")
    finally:
        driver.quit()
        print("Browser closed")

def move_files_to_workspace():
    """Move downloaded files to workspace folder"""
    print("\nMoving files to workspace...")
    
    files = [
        "UTTAR PRADESH.xlsx",
        "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    for filename in files:
        source = Path(DOWNLOAD_FOLDER) / filename
        destination = Path(WORKSPACE_FOLDER) / filename
        
        if source.exists():
            shutil.move(str(source), str(destination))
            print(f"✓ Moved {filename} to workspace")
        else:
            print(f"✗ {filename} not found in downloads")

def push_to_git():
    """Push changes to git repository"""
    print("\nPushing to Git...")
    
    try:
        os.chdir(WORKSPACE_FOLDER)
        
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("No changes to commit")
            return
        
        # Add files
        print("Adding files to git...")
        subprocess.run(['git', 'add', 'UTTAR PRADESH.xlsx', 
                       'All_Schools_with_Notifications_UTTAR PRADESH.xlsx'])
        
        # Commit
        commit_msg = f"Updated Eco Club data - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        print(f"Committing: {commit_msg}")
        subprocess.run(['git', 'commit', '-m', commit_msg])
        
        # Push
        print("Pushing to remote repository...")
        subprocess.run(['git', 'push'])
        
        print("✓ Successfully pushed to Git!")
        
    except Exception as e:
        print(f"Error pushing to Git: {e}")

def main():
    """Main execution function"""
    print("=" * 60)
    print("Eco Club Data Download & Upload Automation")
    print("=" * 60)
    
    # Load credentials
    userid, password = load_credentials()
    
    # Download files
    download_files(userid, password)
    
    # Move files to workspace
    move_files_to_workspace()
    
    # Push to git (DISABLED for testing)
    # push_to_git()
    
    print("\n" + "=" * 60)
    print("Process completed! (Git push disabled for testing)")
    print("=" * 60)

if __name__ == "__main__":
    main()
