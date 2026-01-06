"""
Step by step debug - Browser stays open after each step
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
CHROME_PROFILE = r"d:\Eco club\chrome_profile"

def main():
    print("=" * 70)
    print("STEP-BY-STEP DEBUG MODE")
    print("=" * 70)
    
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 30)
    
    try:
        print(f"\n[1] Opening {WEBSITE_URL}...")
        driver.get(WEBSITE_URL)
        time.sleep(3)
        print("  ✅ Page loaded")
        
        # Download File 1
        print("\n[2] Clicking 'DOWNLOAD STATE WISE DATA EXCEL'...")
        btn1 = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'DOWNLOAD STATE WISE DATA EXCEL')]")
        ))
        btn1.click()
        print("  ✅ Clicked! File should download.")
        time.sleep(5)
        
        # Click notification card
        print("\n[3] Clicking notification card...")
        card = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'boxdivThree')]")
        ))
        card.click()
        print("  ✅ Card clicked!")
        time.sleep(3)
        
        print("\n[4] Checking what happened after card click...")
        print("  Current URL:", driver.current_url)
        
        # Find all buttons on new page
        print("\n  Looking for buttons on current page...")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"\n  Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons, 1):
            if btn.is_displayed():
                text = btn.text.strip()
                if text:
                    print(f"  {i}. '{text}'")
        
        print("\n" + "=" * 70)
        print("BROWSER WILL STAY OPEN FOR 3 MINUTES")
        print("=" * 70)
        print("\nPlease check:")
        print("1. Did page change?")
        print("2. Is there a 'Download All Schools Excel' button?")
        print("3. Tell me what you see!")
        print("\nPress Ctrl+C when done...")
        
        time.sleep(180)
        
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        print("\nBrowser will stay open for 1 minute...")
        time.sleep(60)
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()
