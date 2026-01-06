"""
Complete page analysis - checks iframes, saves page source
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pathlib import Path

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"

def main():
    print("Opening browser...")
    driver = webdriver.Chrome(options=Options())
    driver.maximize_window()
    
    print(f"Loading: {WEBSITE_URL}")
    driver.get(WEBSITE_URL)
    time.sleep(5)
    
    # Save initial page source
    print("\nSaving page source...")
    with open("d:/Eco club/page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("✓ Saved to page_source.html")
    
    # Check for iframes
    print("\nChecking for iframes...")
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print(f"Found {len(iframes)} iframe(s)")
    
    # Try clicking Login button
    print("\nTrying to click Login button...")
    try:
        login_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'adminLogin2') or contains(text(), 'Login')]")
        print(f"Found: {login_btn.text}")
        login_btn.click()
        print("✓ Clicked!")
        time.sleep(3)
        
        # Save page after click
        print("\nSaving page source after click...")
        with open("d:/Eco club/page_after_login_click.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("✓ Saved to page_after_login_click.html")
        
        # Check iframes again
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"\nIframes after click: {len(iframes)}")
        
        # Check for modals
        print("\nLooking for modal/popup...")
        modals = driver.find_elements(By.XPATH, "//*[contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'dialog')]")
        print(f"Found {len(modals)} modal elements")
        
        for i, modal in enumerate(modals, 1):
            if modal.is_displayed():
                print(f"  Modal {i} is VISIBLE!")
                # Try to find inputs in modal
                inputs = modal.find_elements(By.TAG_NAME, "input")
                print(f"    Inputs in modal: {len(inputs)}")
                for inp in inputs:
                    if inp.is_displayed():
                        print(f"      - Type: {inp.get_attribute('type')}, Name: {inp.get_attribute('name')}, Placeholder: {inp.get_attribute('placeholder')}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("Check these files:")
    print("  - page_source.html")
    print("  - page_after_login_click.html")
    print("\nBrowser staying open for manual inspection...")
    print("=" * 60)
    
    time.sleep(300)
    driver.quit()

if __name__ == "__main__":
    main()
