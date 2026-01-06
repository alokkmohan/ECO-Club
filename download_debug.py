"""
Debug version - Browser will stay open and wait for manual intervention
"""

import os
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configuration
WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")

# Load credentials
def load_credentials():
    env_file = Path(r"d:\Eco club") / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    return os.getenv('ECO_USERID'), os.getenv('ECO_PASSWORD')

def setup_driver():
    chrome_options = Options()
    prefs = {
        "download.default_directory": DOWNLOAD_FOLDER,
        "download.prompt_for_download": False,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def main():
    print("=" * 60)
    print("DEBUG MODE - Manual Testing")
    print("=" * 60)
    
    userid, password = load_credentials()
    
    if not userid or not password:
        print("Error: Credentials not found in .env file!")
        return
    
    print("\nStarting Chrome browser...")
    driver = setup_driver()
    
    try:
        print(f"\n1. Opening website: {WEBSITE_URL}")
        driver.get(WEBSITE_URL)
        
        wait = WebDriverWait(driver, 20)
        
        print("\n2. Waiting for login page to load...")
        time.sleep(2)
        
        # Try to find login fields
        print("\n3. Looking for userid field...")
        try:
            userid_field = driver.find_element(By.ID, "userid")
            print("   ✓ Found userid field by ID")
        except:
            print("   ✗ Userid field not found by ID='userid'")
            print("   Trying other selectors...")
            try:
                userid_field = driver.find_element(By.NAME, "userid")
                print("   ✓ Found by NAME='userid'")
            except:
                userid_field = driver.find_element(By.XPATH, "//input[@type='text' or @type='email']")
                print("   ✓ Found by XPATH (first text input)")
        
        print("\n4. Looking for password field...")
        try:
            password_field = driver.find_element(By.ID, "password")
            print("   ✓ Found password field by ID")
        except:
            print("   ✗ Password field not found by ID='password'")
            try:
                password_field = driver.find_element(By.NAME, "password")
                print("   ✓ Found by NAME='password'")
            except:
                password_field = driver.find_element(By.XPATH, "//input[@type='password']")
                print("   ✓ Found by XPATH (password input)")
        
        print("\n5. Entering credentials...")
        userid_field.clear()
        userid_field.send_keys(userid)
        password_field.clear()
        password_field.send_keys(password)
        print("   ✓ Credentials entered")
        
        print("\n6. Looking for login button...")
        try:
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            print("   ✓ Found login button")
        except:
            login_button = driver.find_element(By.XPATH, "//input[@type='submit']")
            print("   ✓ Found login submit button")
        
        print("\n7. Clicking login...")
        login_button.click()
        
        print("\n8. Waiting for login to complete...")
        time.sleep(5)
        
        print("\n" + "=" * 60)
        print("LOGIN COMPLETED!")
        print("=" * 60)
        print("\nNow please:")
        print("1. Check if login was successful")
        print("2. Look at the page and tell me:")
        print("   - Where is 'Download State wise data excel' button?")
        print("   - Where is 'Total Notification Uploaded' button?")
        print("   - What are the exact button names/texts?")
        print("\nBrowser will stay open for 5 minutes for inspection...")
        print("Press Ctrl+C to close early")
        
        # Keep browser open for 5 minutes
        for i in range(300, 0, -30):
            print(f"\rClosing in {i} seconds...", end='')
            time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        print("Browser will stay open for inspection...")
        time.sleep(60)
    finally:
        print("\n\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    main()
