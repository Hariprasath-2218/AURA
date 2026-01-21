import os
import requests

def get_image(query):
    params = {
        "engine": "google_images",
        "q": query,
        "api_key": os.getenv("SERP_API_KEY"),
        "num": 10,
        "safe": "active",
        "img_type": "photo"
    }

    res = requests.get("https://serpapi.com/search", params=params, timeout=10)
    data = res.json()

    for img in data.get("images_results", []):
        url = img.get("original", "")
        if url.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            return url

    raise RuntimeError("No usable image found")
