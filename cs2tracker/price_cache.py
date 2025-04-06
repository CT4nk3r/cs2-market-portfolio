import json
import os
from datetime import datetime, timedelta

CACHE_FILE = "price_cache.json"  # Removed ../
CACHE_DURATION = timedelta(hours=2)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

def get_cached_price(item_name):
    cache = load_cache()
    if item_name in cache:
        entry = cache[item_name]
        timestamp = datetime.fromisoformat(entry["timestamp"])
        if datetime.now() - timestamp < CACHE_DURATION:
            return entry["price"]
    return None

def set_cached_price(item_name, price):
    cache = load_cache()
    cache[item_name] = {
        "price": price,
        "timestamp": datetime.now().isoformat()
    }
    save_cache(cache)