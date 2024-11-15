from curl_cffi import requests
from bs4 import BeautifulSoup
import re
import json
import warnings

warnings.filterwarnings("ignore")

def fetch(dp):
    r = requests.get(f"https://www.amazon.com/dp/{dp}", impersonate="chrome120")
    return r.text

def parse(dp):
    html = fetch(dp)
    
    soup = BeautifulSoup(html, "html.parser")
    
    title_tag = soup.find("span", {"id": "productTitle"})
    title = title_tag.text.strip() if title_tag else "Title not found"
    
    price = None
    span_elements = soup.find_all("span", {"class": "a-offscreen"})
    
    for span in span_elements:
        price_text = span.text.strip()
        if re.match(r"\$\d+(\.\d{2})?", price_text):
            price = price_text
            break
    
    if not price:
        price = "Price not found"
    
    canonical_link_tag = soup.find("link", {"rel": "canonical"})
    link = canonical_link_tag['href'] if canonical_link_tag else "Link not found"
    
    image_gallery = soup.find("div", {"id": "altImages"})
    images = []
    if image_gallery:
        image_tags = image_gallery.find_all("img", {"src": re.compile(r"https://m\.media-amazon\.com/images/I/.*\.jpg")})
        images = [img['src'].split("_")[0] + ".jpg" for img in image_tags if "I" in img['src']]  # Ensuring correct format
    
    store_name_tag = soup.find("a", {"id": "bylineInfo"})
    store_name = store_name_tag.text.strip() if store_name_tag else "Store name not found"
    
    store_link_tag = soup.find("a", {"id": "bylineInfo"})
    store_link = store_link_tag['href'] if store_link_tag else "Store link not found"
    
    about_this_item_section = soup.find("div", {"id": "feature-bullets"})
    about_this_item = []
    if about_this_item_section:
        bullets = about_this_item_section.find_all("span", {"class": "a-list-item"})
        about_this_item = [bullet.text.strip() for bullet in bullets if bullet.text.strip()]
    
    product_details = []
    details_section = soup.find_all("tr", {"class": "a-spacing-small"})
    for detail in details_section:
        label_tag = detail.find("td", {"class": "a-span3"})
        value_tag = detail.find("td", {"class": "a-span9"})
        if label_tag and value_tag:
            label = label_tag.text.strip()
            value = value_tag.text.strip()
            product_details.append([label, value])
    
    description_tag = soup.find("div", {"id": "productDescription"})
    product_description = description_tag.text.strip() if description_tag else "Description not found"

    whats_in_the_box = None
    
    keywords = ["What's in the Box", "Included", "Box Contains"]
    
    for keyword in keywords:
        possible_section = soup.find(text=re.compile(keyword, re.IGNORECASE))
        if possible_section:
            whats_in_the_box_section = possible_section.find_parent().find_next_sibling()
            if whats_in_the_box_section:
                whats_in_the_box = whats_in_the_box_section.get_text(strip=True)
                break
    
    if not whats_in_the_box:
        whats_in_the_box = "Not found"

    output = {
        "message": "Scrape operation completed successfully.",
        "status": "success",
        "details": {
            "title": title,
            "price": price,
            "rrp": None,
            "discount": None,
            "link": link,
            "images": images,
            "seller_info": {
                "store_name": store_name,
                "store_link": store_link
            },
            "about_this_item": about_this_item,
            "product_details": product_details,
            "document_url": None,
            "whats_in_the_box": whats_in_the_box,
            "product_description": product_description
        }
    }

    print(json.dumps(output, indent=4))

parse("B0C9PNZJCF")
