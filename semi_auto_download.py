"""
Semi-Automated Download - Login once, then auto-download
Session persists so you don't need to login again
"""

import os
import time
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")
WORKSPACE_FOLDER = r"d:\Eco club"

def setup_driver():
    """Setup Chrome with download preferences"""
    chrome_options = Options()
    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def wait_for_download(filename, timeout=60):
    """Wait for file to complete downloading"""
    file_path = Path(DOWNLOAD_FOLDER) / filename
    
    print(f"  Waiting for {filename}...", end='', flush=True)
    
    for i in range(timeout):
        if file_path.exists():
            # File exists, wait a bit more to ensure complete
            time.sleep(2)
            print(" ✓ Downloaded!")
            return True
        print(".", end='', flush=True)
        time.sleep(1)
    
    print(" ✗ Timeout!")
    return False

def download_files(driver, wait):
    """Click download buttons and wait for downloads"""
    
    print("\n" + "=" * 60)
    print("DOWNLOADING FILES")
    print("=" * 60)
    
    # Download File 1: UTTAR PRADESH.xlsx
    print("\n1. Downloading UTTAR PRADESH.xlsx...")
    try:
        download_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download State Wise Data Excel')]"))
        )
        download_btn.click()
        
        if wait_for_download("UTTAR PRADESH.xlsx"):
            print("  ✓ Success!")
        else:
            print("  ✗ Failed - file not found in Downloads")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    time.sleep(2)
    
    # Download File 2: All_Schools_with_Notifications_UTTAR PRADESH.xlsx
    print("\n2. Downloading All_Schools_with_Notifications_UTTAR PRADESH.xlsx...")
    try:
        # Try finding button by class
        print("  Looking for 'Download All Schools Excel' button...")
        download_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-warning') and contains(text(), 'Download All Schools Excel')]"))
        )
        download_btn.click()
        print("  ✓ Clicked!")
        
        if wait_for_download("All_Schools_with_Notifications_UTTAR PRADESH.xlsx"):
            print("  ✓ Success!")
        else:
            print("  ✗ Failed - file not found in Downloads")
            
    except Exception as e:
        print(f"  ✗ Error: {e}")

def move_files_to_workspace():
    """Move downloaded files from Downloads to workspace"""
    print("\n" + "=" * 60)
    print("MOVING FILES TO WORKSPACE")
    print("=" * 60)
    
    files = [
        "UTTAR PRADESH.xlsx",
        "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
    ]
    
    for filename in files:
        source = Path(DOWNLOAD_FOLDER) / filename
        destination = Path(WORKSPACE_FOLDER) / filename
        
        if source.exists():
            shutil.move(str(source), str(destination))
            print(f"✓ Moved {filename}")
        else:
            print(f"✗ {filename} not found in Downloads folder")

def main():
    print("=" * 60)
    print("SEMI-AUTOMATED ECO CLUB DATA DOWNLOADER")
    print("=" * 60)
    
    print("\nStarting Chrome browser...")
    driver = setup_driver()
    wait = WebDriverWait(driver, 20)
    
    try:
        print(f"Opening: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)
        
        print("\n" + "=" * 60)
        print("MANUAL LOGIN REQUIRED")
        print("=" * 60)
        print("\nPlease LOGIN to the website now.")
        print("After successful login, press ENTER here to continue...")
        input()
        
        # Now download files automatically
        download_files(driver, wait)
        
        # Move files to workspace
        move_files_to_workspace()
        
        print("\n" + "=" * 60)
        print("DOWNLOAD COMPLETE!")
        print("=" * 60)
        print("\nOptions:")
        print("1. Keep browser open for next download (press Enter)")
        print("2. Close browser (type 'exit' and press Enter)")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'exit':
            driver.quit()
            print("Browser closed.")
        else:
            print("\nBrowser staying open...")
            print("Run this script again to download without logging in!")
            print("(Make sure to delete old files from Downloads first)")
            input("\nPress Enter when done to close browser...")
            driver.quit()
    
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to close...")
        driver.quit()

if __name__ == "__main__":
    main()
