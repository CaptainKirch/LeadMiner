from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import re

keywords = [
    "accountants near Penticton British Columbia",
    "law offices near Penticton British Columbia",
    "gyms near Penticton British Columbia",
    "nail salons near Penticton British Columbia",
    "botox clinics near Penticton British Columbia",
    "dentist practices near Penticton British Columbia",
    "property managers near Penticton British Columbia",
    "massage therapy near Penticton British Columbia",
    "dance studios near Penticton British Columbia",
    "physiotherapy near Penticton British Columbia",
    "real estate offices near Penticton British Columbia",
    "mortgage brokers near Penticton British Columbia",
    "manufacturing businesses near Penticton British Columbia",
    "construction businesses near Penticton British Columbia",
    "plumbing companies near Penticton British Columbia",
    "industrial buildings near Penticton British Columbia",
    "commercial real estate near Penticton British Columbia",
    "accountants near Kelowna British Columbia",
    "law offices near Kelowna British Columbia",
    "gyms near Kelowna British Columbia",
    "nail salons near Kelowna British Columbia",
    "botox clinics near Kelowna British Columbia",
    "dentist practices near Kelowna British Columbia",
    "property managers near Kelowna British Columbia",
    "massage therapy near Kelowna British Columbia",
    "dance studios near Kelowna British Columbia",
    "physiotherapy near Kelowna British Columbia",
    "real estate offices near Kelowna British Columbia",
    "mortgage brokers near Kelowna British Columbia",
    "manufacturing businesses near Kelowna British Columbia",
    "construction businesses near Kelowna British Columbia",
    "plumbing companies near Kelowna British Columbia",
    "industrial buildings near Kelowna British Columbia",
    "commercial real estate near Kelowna British Columbia",
    "accountants near West Kelowna British Columbia",
    "law offices near West Kelowna British Columbia",
    "gyms near West Kelowna British Columbia",
    "nail salons near West Kelowna British Columbia",
    "botox clinics near West Kelowna British Columbia",
    "dentist practices near West Kelowna British Columbia",
    "property managers near West Kelowna British Columbia",
    "massage therapy near West Kelowna British Columbia",
    "dance studios near West Kelowna British Columbia",
    "physiotherapy near West Kelowna British Columbia",
    "real estate offices near West Kelowna British Columbia",
    "mortgage brokers near West Kelowna British Columbia",
    "manufacturing businesses near West Kelowna British Columbia",
    "construction businesses near West Kelowna British Columbia",
    "plumbing companies near West Kelowna British Columbia",
    "industrial buildings near West Kelowna British Columbia",
    "commercial real estate near West Kelowna British Columbia"
]

options = Options()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
options.add_argument("--window-size=1920,1080")
# options.add_argument("--headless=new")

service = Service("./chromedriver")
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

def scroll_page():
    try:
        for _ in range(20):
            scrollable = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
            time.sleep(2)
    except Exception as e:
        print("❌ Scroll error:", e)


def scrape_full_listing():
    try:
        name = driver.find_element(By.XPATH, '//h1').text.strip()
    except:
        name = "N/A"

    # PHONE: Try XPath, fallback XPath, then regex
# PHONE: Try modern selectors and regex fallback
    phone = "N/A"
    try:
    # Try common phone button or span
        phone_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Phone") or contains(@aria-label, "Call")]')
        raw_phone = phone_elem.get_attribute("aria-label")
        phone = raw_phone.split(":")[-1].strip() if raw_phone else "N/A"
    except:
        try:
        # Try any span or div with visible phone number format
            phone_elem_alt = driver.find_element(By.XPATH, '//span[contains(text(), "(") and contains(text(), ")")]')
            phone = phone_elem_alt.text.strip()
        except:
            try:
                page_text = driver.page_source
                match = re.search(r"\(?\d{3}\)?[\s\.\-]?\d{3}[\s\.\-]?\d{4}", page_text)
                phone = match.group() if match else "N/A"
            except:
                phone = "N/A"


    if phone == "N/A":
        print("\n⚠️ DEBUG: Could not find phone, dumping HTML...")
        print(driver.page_source[:3000])

    try:
        website_elem = driver.find_element(By.XPATH, '//a[contains(@aria-label, "Website")]')
        website = website_elem.get_attribute("href")
    except:
        website = "N/A"

    try:
        address_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Address")]')
        address = address_elem.get_attribute("aria-label").split(":")[-1].strip()
    except:
        address = "N/A"

    try:
        rating_elem = driver.find_element(By.XPATH, '//span[contains(@aria-label, "stars")]')
        rating = rating_elem.get_attribute("aria-label")
    except:
        rating = "N/A"

    try:
        category_elem = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Category")]')
        category = category_elem.get_attribute("aria-label").split(":")[-1].strip()
    except:
        category = "N/A"

    return name, phone, website, address, rating, category

def main():
    results = []

    for keyword in keywords:
        search_url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}"
        print(f"\n🔍 Opening: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        scroll_page()

        business_links = set()
        cards = driver.find_elements(By.XPATH, '//a[contains(@href, "/place/")]')
        for card in cards:
            link = card.get_attribute("href")
            if link and link.startswith("https://www.google.com/maps/place/"):
                business_links.add(link)

        print(f"🔗 Found {len(business_links)} listings to click for '{keyword}'")

        for link in business_links:
            try:
                driver.get(link)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1")))
                time.sleep(6)
                name, phone, website, address, rating, category = scrape_full_listing()
                results.append({
                    "Keyword": keyword,
                    "Name": name,
                    "Phone": phone,
                    "Website": website,
                    "Address": address,
                    "Rating": rating,
                    "Category": category,
                    "GoogleMapsURL": link
                })
                print(f"✅ {name} | {phone} | {website} | {address} | {rating} | {category}")
                time.sleep(2)
            except Exception as e:
                print(f"❌ Failed to scrape listing: {link}", e)

    os.makedirs("output", exist_ok=True)
    with open("output/results_clickin_v2.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Keyword", "Name", "Phone", "Website", "Address", "Rating", "Category", "GoogleMapsURL"])
        writer.writeheader()
        writer.writerows(results)

    driver.quit()
    print("✅ Scraping complete. Results saved to output/results_clickin_v2.csv")

if __name__ == "__main__":
    main()