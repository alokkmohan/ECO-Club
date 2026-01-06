"""
Complete Page Inspector - Shows all clickable elements
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pathlib import Path

WEBSITE_URL = "https://ecoclubs.education.gov.in/Ekpedmaakenaam"

def main():
    print("=" * 60)
    print("Page Element Inspector")
    print("=" * 60)
    
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    print(f"\nOpening: {WEBSITE_URL}")
    driver.get(WEBSITE_URL)
    time.sleep(3)
    
    print("\n" + "=" * 60)
    print("LOGIN PAGE ANALYSIS")
    print("=" * 60)
    
    # Find all input fields
    print("\n--- INPUT FIELDS ---")
    inputs = driver.find_elements(By.TAG_NAME, "input")
    for i, inp in enumerate(inputs, 1):
        input_type = inp.get_attribute("type")
        input_id = inp.get_attribute("id")
        input_name = inp.get_attribute("name")
        input_placeholder = inp.get_attribute("placeholder")
        print(f"{i}. Type: {input_type}, ID: {input_id}, Name: {input_name}, Placeholder: {input_placeholder}")
    
    # Find all buttons
    print("\n--- BUTTONS ---")
    buttons = driver.find_elements(By.TAG_NAME, "button")
    for i, btn in enumerate(buttons, 1):
        btn_text = btn.text
        btn_type = btn.get_attribute("type")
        btn_class = btn.get_attribute("class")
        print(f"{i}. Text: '{btn_text}', Type: {btn_type}, Class: {btn_class}")
    
    print("\n" + "=" * 60)
    print("Copy this information and send it to me!")
    print("Browser will stay open for 2 minutes...")
    print("=" * 60)
    
    time.sleep(120)
    driver.quit()
    print("\nDone!")

if __name__ == "__main__":
    main()
