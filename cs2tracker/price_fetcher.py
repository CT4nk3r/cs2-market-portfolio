import requests
import time
import re
from .price_cache import get_cached_price, set_cached_price

def get_steam_price(item_name):
    # Check cache first
    cached_price = get_cached_price(item_name)
    if cached_price is not None:
        print(f"Using cached price for {item_name}: {cached_price}")
        return cached_price

    url = "http://steamcommunity.com/market/priceoverview/"
    params = {
        "appid": 730,  # CS:GO
        "currency": 3,  # EUR
        "market_hash_name": item_name
    }
    full_url = requests.Request('GET', url, params=params).prepare().url
    print(f"Requesting: {full_url}")
    
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Response for {item_name}: {data}")
                price = data.get("lowest_price", "No Listings") if data.get("success") else "N/A"
                set_cached_price(item_name, price)  # Cache the result
                return price
            elif response.status_code == 429:
                print(f"Rate limit hit for {item_name}, waiting 60s...")
                time.sleep(60)
            else:
                return f"Error {response.status_code}: {response.text}"
        except requests.RequestException as e:
            return f"Error: {str(e)}"
    return "Rate Limit Exceeded"

def clean_price(price_str):
    """Convert euro price strings (e.g., '4,43€') to float."""
    if price_str in ["No Listings", "N/A", "Rate Limit Exceeded"] or "Error" in price_str:
        return price_str
    cleaned = re.sub(r'[^\d,.]', '', price_str).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return 0.00