"""
Super Simple - Just opens browser, you login manually
Then we can inspect the page to find correct element selectors
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")

def main():
    print("=" * 60)
    print("Manual Testing Mode")
    print("=" * 60)
    
    chrome_options = Options()
    prefs = {"download.default_directory": DOWNLOAD_FOLDER}
    chrome_options.add_experimental_option("prefs", prefs)
    
    print("\nOpening Chrome browser...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    print(f"Loading website: {WEBSITE_URL}")
    driver.get(WEBSITE_URL)
    
    print("\n" + "=" * 60)
    print("BROWSER IS OPEN!")
    print("=" * 60)
    print("\nPlease do the following MANUALLY:")
    print("1. Login to the website")
    print("2. Navigate to where the download buttons are")
    print("3. RIGHT-CLICK on 'Download State wise data excel' button")
    print("4. Select 'Inspect' (or press F12)")
    print("5. Tell me what you see in the HTML")
    print("\nBrowser will stay open for 10 minutes...")
    print("Press Ctrl+C to close anytime")
    print("=" * 60)
    
    try:
        for i in range(600, 0, -30):
            print(f"\rTime remaining: {i//60}:{i%60:02d}", end='', flush=True)
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n\nClosing browser...")
    finally:
        driver.quit()
        print("Done!")

if __name__ == "__main__":
    main()
