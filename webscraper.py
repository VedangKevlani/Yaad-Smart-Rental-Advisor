import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Target website
# url = "https://century21jm.com/search/residential-commercial/residential/rent-sale/rent/parish/parish/town/town/property-type/property-type/currency/currency/id-search/id-search/sqft_total/sqft_total/bed/bed/bath/bath/search/search/from/from/to/to/page/4/limit/12/range/H"

# Make folder if not exists
folder = "property_dataset/real"
os.makedirs(folder, exist_ok=True)

# Start counting from the last image number in the folder
existing_files = os.listdir(folder)
existing_numbers = [int(f.split("_")[1].split(".")[0]) for f in existing_files if f.startswith("real_") and f.endswith(".jpg")]
count = max(existing_numbers, default=-1) + 1

for page_num in range(1, 11):  
    url = "https://jamaicaclassifiedonline.com/?s=&category=houses&type=2&sort=&currency=JMD&price=&parish=kingston_st_andrew&orderby=modified_date&recent="    
    print("Fetching page", page_num)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    print("Status code:", response.status_code)
    soup = BeautifulSoup(response.text, "html.parser")
    img_tags = soup.find_all("img")

    print("Found", len(img_tags), "images")
    for img in img_tags:
        print("IMG TAG:", img)
        img_url = img.get("src") or img.get("data-src")
        if img_url and ("/images/" in img_url):  # Only scrape images from /images/ folder
            if img_url and ("png" in img_url or "jpg" in img_url or "jpeg" in img_url):
                full_url = urljoin(url, img_url)
                try:
                    img_data = requests.get(full_url).content
                    with open(f"{folder}/real_{count}.jpg", "wb") as f:
                        f.write(img_data)
                        print(f"Saved real_{count}.jpg")
                        count += 1
                    if count >= 200: 
                        break
                except Exception as e:
                    print(f"Failed to download {img_url}: {e}")
    if count >= 200:
        break


print(f"Downloaded {count} real images.")