# scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import os

from utils import (
    wait_for_element,
    get_text_or_blank,
    split_quantity_unit,
    smart_sleep
)

# Setting up selenium chromedriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    service = Service(executable_path="C://Users//Abhinav//Desktop//Pytask//chromedriver-win64//chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# scrape a single page of RFQs
def scrape_page(driver):
    wait_for_element(driver, By.XPATH, '//div[contains(@class, "brh-rfq-item")]', timeout=15)

    items = driver.find_elements(By.XPATH, '//div[contains(@class, "brh-rfq-item")]')
    print(f"[i] Found {len(items)} RFQs on this page")

    data = []
    for item in items:
        title = get_text_or_blank(item, By.CLASS_NAME, "brh-rfq-item__subject-link")
        description = get_text_or_blank(item, By.CLASS_NAME, "brh-rfq-item__detail")
        quantity_text = get_text_or_blank(item, By.CLASS_NAME, "brh-rfq-item__quantity-num")
        country = get_text_or_blank(item, By.CLASS_NAME, "brh-rfq-item__country")
        user_name = get_text_or_blank(item, By.CLASS_NAME, "text")
        quotes_left = get_text_or_blank(item, By.CLASS_NAME, "brh-rfq-item__quote-left").replace("Quotes Left", "").strip()
        posted_time = get_text_or_blank(item, By.CLASS_NAME, "brh-rfq-item__publishtime").replace("Date Posted:", "").strip()

        email_verified = "Yes" if "Email Confirmed" in item.get_attribute("innerHTML") else "No"

        qty, unit = split_quantity_unit(quantity_text)

        data.append({
            "Title": title,
            "Description": description,
            "Quantity": qty,
            "Unit": unit,
            "Country": country,
            "User Name": user_name,
            "Email Verified": email_verified,
            "Quotes Left": quotes_left,
            "Date Posted": posted_time
        })

    return data

# click next page button
def go_to_next_page(driver):
    try:
        next_btn = driver.find_element(By.CLASS_NAME, "ui2-pagination-next")
        if "ui2-pagination-disabled" in next_btn.get_attribute("class"):
            return False
        next_btn.click()
        smart_sleep(2, 4)
        return True
    except NoSuchElementException:
        return False

# scrape all pages
def scraper_all_pages():
    driver = setup_driver()
    driver.get("https://sourcing.alibaba.com/rfq/rfq_search_list.htm?country=AE&recently=Y")

    smart_sleep(4, 6)

    all_data = []
    page = 1

    while True:
        print(f"\nScraping page {page}...")
        page_data = scrape_page(driver)
        print(f"Found {len(page_data)} RFQs on page {page}")
        all_data.extend(page_data)

        if not go_to_next_page(driver):
            break
        page += 1

    driver.quit()

    if not all_data:
        print("\nNo RFQ data was scraped. Please verify page structure or class names.")
        return

    # save to CSV
    df = pd.DataFrame(all_data)
    os.makedirs("output", exist_ok=True)
    df.to_csv("output/alibaba_rfq.csv", index=False)
    print(f"\nScraping complete. {len(all_data)} records saved to 'output directory'")


