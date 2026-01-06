"""
Click Login button then inspect form fields
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"

def main():
    print("Opening browser...")
    driver = webdriver.Chrome(options=Options())
    driver.maximize_window()
    
    print(f"Loading: {WEBSITE_URL}")
    driver.get(WEBSITE_URL)
    time.sleep(3)
    
    print("\nLooking for Login button...")
    try:
        login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        print(f"Found Login button: {login_btn.text}")
        print("Clicking...")
        login_btn.click()
        time.sleep(3)
        
        print("\n" + "=" * 60)
        print("LOGIN FORM FIELDS")
        print("=" * 60)
        
        # Find all input fields after clicking Login
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"\nFound {len(inputs)} input fields:")
        for i, inp in enumerate(inputs, 1):
            input_type = inp.get_attribute("type")
            input_id = inp.get_attribute("id")
            input_name = inp.get_attribute("name")
            input_placeholder = inp.get_attribute("placeholder")
            input_class = inp.get_attribute("class")
            is_visible = inp.is_displayed()
            print(f"\n{i}. Visible: {is_visible}")
            print(f"   Type: {input_type}")
            print(f"   ID: {input_id}")
            print(f"   Name: {input_name}")
            print(f"   Placeholder: {input_placeholder}")
            print(f"   Class: {input_class}")
        
        # Find submit button
        print("\n--- SUBMIT BUTTONS ---")
        buttons = driver.find_elements(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
        for i, btn in enumerate(buttons, 1):
            if btn.is_displayed():
                print(f"{i}. Text: '{btn.text}', Tag: {btn.tag_name}, Class: {btn.get_attribute('class')}")
        
        print("\n" + "=" * 60)
        print("Browser will stay open for 3 minutes...")
        print("Inspect manually if needed!")
        print("=" * 60)
        
        time.sleep(180)
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(60)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
