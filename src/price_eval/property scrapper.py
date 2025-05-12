from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

data = []

for page in range(1, 31):
    url = f"https://www.getkeez.com/search?page={page}&sort=distance&ll=18.0028,-76.7897&property_type=apartment&rent_sale=rent"
    driver.get(url)
    print(f"Scraping page {page}...")
    time.sleep(5)

    properties = driver.find_elements(By.CLASS_NAME, "col")

    if not properties:
        print(f"No properties found on page {page}. Ending scrape.")
        break

    for i, prop in enumerate(properties, start=1):
        try:
            price_div = prop.find_element(By.CLASS_NAME, "price")
            currency = price_div.find_element(By.CLASS_NAME, "currency").text
            price = price_div.text.replace(currency, "").strip()
        except:
            currency = ""
            price = ""

        try:
            address_link = prop.find_element(By.CLASS_NAME, "address").find_element(By.TAG_NAME, "a")
            address = address_link.text.strip()
            link = address_link.get_attribute("href")
        except:
            address = ""
            link = ""

        try:
            state = prop.find_element(By.CLASS_NAME, "state").text.strip()
            parish = state.split(",")[-1].strip()
        except:
            state = ""
            parish = ""

        try:
            specs = prop.find_element(By.CLASS_NAME, "specs").text
            sqft = specs.split("·")[-1].strip() if "sqft" in specs else ""
        except:
            sqft = ""

        # print(f"  Property {i} on page {page}")
        # print(f"    Currency: {currency}")
        # print(f"    Price: {price}")
        # print(f"    Address: {address}")
        # print(f"    State: {state}")
        # print(f"    Parish: {parish}")
        # print(f"    Square Footage: {sqft}")
        # print(f"    Link: {link}")

        data.append({
            "Currency": currency,
            "Price": price,
            "Address": address,
            "State": state,
            "Parish": parish,
            "Square Footage": sqft,
            "Link": link
        })

driver.quit()

df = pd.DataFrame(data)
df.to_csv("keez_rentals_all_pages.csv", index=False)
print(f"\n✅ Finished scraping. {len(data)} listings saved to keez_rentals_all_pages.csv")
