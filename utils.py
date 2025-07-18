from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException,NoSuchElementException
import time
import  random

def wait_for_element(driver,by_type,value,timeout=10):
    try:
        wait = WebDriverWait(driver,timeout)
        element = wait.until(ec.presence_of_all_elements_located((by_type,value)))
        return element
    except TimeoutException:
        print(f"Timeout: Element {value} not found")
        return None

def get_text_or_blank(parent,by_type,value):
    try:
        return parent.find_element(by_type,value).text.strip()
    except NoSuchElementException:
        return ""

def clean_text(text):
    return text.replace("\n"," ").replace("\r","").strip()

def split_quantity_unit(text):
    parts = text.strip().split(" ",1)
    if len(parts) == 2:
        return parts[0],parts[1]

    elif len(parts) == 1:
        return parts[0],""
    else:
        return "",""

def smart_sleep(min_seconds=2,max_seconds=5):
    t = random.uniform(min_seconds,max_seconds)
    print(f"[i] Sleeps for {round(t,2)} secondss..")
    time.sleep(t)
    