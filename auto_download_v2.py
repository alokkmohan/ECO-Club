"""
Eco Club Auto Downloader - Fixed version
Steps:
1. Login manually
2. On home page: Click "Download State Wise Data Excel" → UTTAR PRADESH
3. Click on "Total Notifications Uploaded" card/number
4. Click "Download All Schools Excel" → All notifications file
"""

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
    print(f"    Waiting for {filename}...", end='', flush=True)
    
    for i in range(timeout):
        if file_path.exists():
            time.sleep(2)  # Wait for complete
            print(" ✓")
            return True
        print(".", end='', flush=True)
        time.sleep(1)
    
    print(" ✗ Timeout!")
    return False

def main():
    print("=" * 70)
    print("ECO CLUB AUTO DOWNLOADER v2")
    print("=" * 70)
    
    driver = setup_driver()
    wait = WebDriverWait(driver, 30)
    
    try:
        print(f"\n[1] Opening website: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)
        time.sleep(3)
        
        print("\n[2] Please LOGIN manually now...")
        print("    After successful login, press ENTER to continue...")
        input()
        
        print("\n[3] Waiting for home page to load...")
        time.sleep(3)
        
        # DOWNLOAD FILE 1: UTTAR PRADESH.xlsx
        print("\n" + "=" * 70)
        print("DOWNLOADING FILE 1: UTTAR PRADESH.xlsx")
        print("=" * 70)
        
        print("\n[4] Looking for 'Download State Wise Data Excel' button...")
        try:
            # Try multiple selectors
            btn = None
            try:
                btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Download State Wise Data Excel')]")
                ))
                print("    ✓ Found button!")
            except:
                print("    ! Trying alternate selector...")
                btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Download')]")
                ))
                print("    ✓ Found button!")
            
            print("\n[5] Clicking download button...")
            btn.click()
            print("    ✓ Clicked!")
            
            print("\n[6] Waiting for download...")
            if wait_for_download("UTTAR PRADESH.xlsx", 60):
                print("    ✓ File 1 downloaded successfully!")
            else:
                print("    ✗ File 1 download failed or timeout")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
        
        time.sleep(3)
        
        # DOWNLOAD FILE 2: All_Schools_with_Notifications_UTTAR PRADESH.xlsx
        print("\n" + "=" * 70)
        print("DOWNLOADING FILE 2: All_Schools_with_Notifications_UTTAR PRADESH.xlsx")
        print("=" * 70)
        
        print("\n[7] Looking for 'Total Notifications Uploaded' button with bell icon...")
        try:
            # Look for button/element with bell icon and notification text
            notification_elem = None
            try:
                # Try finding by text (most specific)
                notification_elem = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Total Notification') or contains(text(), 'Total Notification Uploaded')]")
                ))
                print("    ✓ Found button by text!")
            except:
                print("    ! Trying to find by bell icon...")
                try:
                    # Try finding element containing SVG (bell icon)
                    notification_elem = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), 'Total Notification')]//ancestor::button | //button[contains(., 'Total Notification')]")
                    ))
                    print("    ✓ Found button with icon!")
                except:
                    # Try any clickable element with notification text
                    notification_elem = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(), 'Notification') and contains(text(), 'Upload')]")
                    ))
                    print("    ✓ Found notification element!")
            
            print("\n[8] Clicking 'Total Notifications Uploaded'...")
            notification_elem.click()
            print("    ✓ Clicked!")
            time.sleep(3)
            
            print("\n[9] Looking for 'Download All Schools Excel' button...")
            download_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Download All Schools Excel')]")
            ))
            print("    ✓ Found button!")
            
            print("\n[10] Clicking download button...")
            download_btn.click()
            print("    ✓ Clicked!")
            
            print("\n[11] Waiting for download...")
            if wait_for_download("All_Schools_with_Notifications_UTTAR PRADESH.xlsx", 60):
                print("    ✓ File 2 downloaded successfully!")
            else:
                print("    ✗ File 2 download failed or timeout")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
            print("\n    If button not found, you may need to:")
            print("    - Go back to home page")
            print("    - Or manually click and then continue")
        
        # MOVE FILES TO WORKSPACE
        print("\n" + "=" * 70)
        print("MOVING FILES TO WORKSPACE")
        print("=" * 70)
        
        files = [
            "UTTAR PRADESH.xlsx",
            "All_Schools_with_Notifications_UTTAR PRADESH.xlsx"
        ]
        
        for filename in files:
            source = Path(DOWNLOAD_FOLDER) / filename
            destination = Path(WORKSPACE_FOLDER) / filename
            
            if source.exists():
                shutil.move(str(source), str(destination))
                print(f"✓ Moved: {filename}")
            else:
                print(f"✗ Not found: {filename}")
        
        print("\n" + "=" * 70)
        print("PROCESS COMPLETE!")
        print("=" * 70)
        
        print("\nKeep browser open? (Press Enter to keep, type 'exit' to close)")
        choice = input().strip().lower()
        
        if choice != 'exit':
            print("\nBrowser will stay open. Press Enter when done...")
            input()
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        input("Press Enter to close...")
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()
