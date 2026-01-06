"""
Complete page inspector - shows ALL clickable elements after login
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"
CHROME_PROFILE = r"d:\Eco club\chrome_profile"

def main():
    print("=" * 70)
    print("PAGE ELEMENT INSPECTOR")
    print("=" * 70)
    
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={CHROME_PROFILE}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    print(f"\nOpening {WEBSITE_URL}...")
    driver.get(WEBSITE_URL)
    time.sleep(5)
    
    print("\n" + "=" * 70)
    print("ALL BUTTONS ON PAGE:")
    print("=" * 70)
    
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\nFound {len(buttons)} buttons:\n")
    
    for i, btn in enumerate(buttons, 1):
        if btn.is_displayed():
            text = btn.text.strip()
            classes = btn.get_attribute("class")
            onclick = btn.get_attribute("onclick")
            print(f"{i}. TEXT: '{text}'")
            print(f"   CLASS: {classes}")
            if onclick:
                print(f"   ONCLICK: {onclick}")
            print()
    
    print("\n" + "=" * 70)
    print("ALL DIVS WITH NUMBERS (cards/stats):")
    print("=" * 70)
    
    divs = driver.find_elements(By.TAG_NAME, "div")
    for i, div in enumerate(divs, 1):
        if div.is_displayed():
            text = div.text.strip()
            if text and any(keyword in text.lower() for keyword in ['total', 'notification', 'upload', 'school']):
                classes = div.get_attribute("class")
                print(f"{i}. TEXT: '{text[:100]}'")
                print(f"   CLASS: {classes}")
                print()
    
    print("\n" + "=" * 70)
    print("Saving page source to file...")
    print("=" * 70)
    
    with open("d:/Eco club/page_source_logged_in.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    
    print("✅ Saved to: page_source_logged_in.html")
    
    print("\nBrowser will stay open for 2 minutes for manual inspection...")
    time.sleep(120)
    
    driver.quit()
    print("\nDone!")

if __name__ == "__main__":
    main()
