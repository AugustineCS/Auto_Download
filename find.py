import os
import requests
import time
import logging
from playwright.sync_api import sync_playwright

# Input what image is to be downloaded
KEYWORD = "cat"

save_dir = rf"C:\ubuntu\pro\PlayWright_Python\images\{KEYWORD}"
os.makedirs(save_dir, exist_ok=True)
idx = 1

# LOGGING
logging.basicConfig(
    level=logging.INFO,
    format=("%(asctime)s [%(levelname)s] %(message)s")
)


def download_image(url, folder, idx):
    """
    Download function , which takes a particular url, path, index unmber.
    It only downloads a particular url to a particular path
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        if (
            response.status_code == 200
            and "image" in response.headers.get("Content-Type", "")
        ):
            file_path = os.path.join(folder, f"{KEYWORD}_{idx}.jpg")
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            logging.info(f"Downloaded: {file_path}")
        else:
            logging.warning(f"Skipped: {url}")
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=100)
    page = browser.new_page(ignore_https_errors=True)
    page.goto(f"https://pixabay.com/photos/search/{KEYWORD}/", timeout=60000)

    """
    a[href^='/photos/'] img
    it search for images with <img> tag which is inside <a> tag
    and its href starts with /photos/
    By using it we can avoid downloading thumbnails and unwanted ads and images
    """
    page.wait_for_selector("a[href^='/photos/'] img", timeout=30000)
    img_urls = set()
    unchanged_scrolls = 0
    scroll_round = 0

    while len(img_urls) < 100 and unchanged_scrolls < 5:
        scroll_round += 1                      # Scrolling to load more images
        logging.info(f"Scrolling round {scroll_round}...")
        page.evaluate("window.scrollBy(0, window.innerHeight)")
        time.sleep(3)

        img_elements = page.query_selector_all("a[href^='/photos/'] img")

        before_count = len(img_urls)
        for img in img_elements:
            """
            Inside the image tag there are src, srcset
            src = only one image, we take it as url and download it
                  url = src
            srcset = 2,3 images may prsent in which the last image is the best
                     So we download last image and set it to url
                     url = srcset.split(",")[-1].split()[0]
            """
            srcset = img.get_attribute("srcset")
            src = img.get_attribute("src")
            url = None
            if srcset:
                url = srcset.split(",")[-1].split()[0]
            elif src:
                url = src
            if url and url.startswith("https://cdn.pixabay.com/photo/"):
                img_urls.add(url)

        after_count = len(img_urls)
        logging.info(f"Found {after_count} unique images so far")

        if after_count == before_count:
            unchanged_scrolls += 1
        else:
            unchanged_scrolls = 0

    logging.info(f"\nTotal {KEYWORD} images collected: {len(img_urls)}")

    """
    looping download_image function so that we can iterate
    it and download 100 images
    """
    for url in list(img_urls)[:100]:
        download_image(url, save_dir, idx)
        idx += 1

    browser.close()
