import requests
import csv
import time
import re
import os
from datetime import datetime

def get_steam_price(item_name):
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
                return data.get("lowest_price", "No Listings") if data.get("success") else "N/A"
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

def process_armory_pass(armory_file, pass_price):
    stars_per_euro = 40 / pass_price
    with open(armory_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        armory_items = list(reader)
    
    # Load inventory
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        items = list(reader)
    
    # Move Armory Pass items to inventory with star-converted price
    for armory_item in armory_items:
        if armory_item["Acquisition Method"] != "One-Time Purchase":  # Skip the pass itself
            stars_used = int(armory_item["Stars Used"])
            price_in_euros = round(stars_used / stars_per_euro, 2)
            items.append({
                "Count": armory_item["Count"],
                "Item Name": armory_item["Item Name"],
                "Price Bought At": str(price_in_euros),
                "Acquisition Method": armory_item["Acquisition Method"]
            })
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    processed_dir = "armory_pass/processed"
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(armory_file, f"{processed_dir}/{os.path.basename(armory_file)}")
    print(f"Processed armory pass: {armory_file}")

def process_tradeup(tradeup_file):
    with open(tradeup_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        tradeup_items = list(reader)
    
    output_item = next(item for item in tradeup_items if item["Acquisition Method"] == "Trade-Up")
    
    # Add output to inventory
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        items = list(reader)
    
    items.append({
        "Count": output_item["Count"],
        "Item Name": output_item["Item Name"],
        "Price Bought At": output_item["Price Bought At"],
        "Acquisition Method": output_item["Acquisition Method"]
    })
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    processed_dir = "tradeups/processed"
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(tradeup_file, f"{processed_dir}/{os.path.basename(tradeup_file)}")
    print(f"Processed trade-up: {tradeup_file}")

def process_case_opening(case_file):
    with open(case_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        case_data = next(reader)
    
    outcome_item = {"name": case_data["Outcome Item"]}
    
    # Add outcome to inventory
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        items = list(reader)
    
    items.append({
        "Count": "1",
        "Item Name": outcome_item["name"],
        "Price Bought At": "0.00",
        "Acquisition Method": "Case Opening"
    })
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    processed_dir = "case_openings/processed"
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(case_file, f"{processed_dir}/{os.path.basename(case_file)}")
    print(f"Processed case opening: {case_file}")

def process_sale(sale_file):
    processed_dir = "sales/processed"
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(sale_file, f"{processed_dir}/{os.path.basename(sale_file)}")
    print(f"Processed sale: {sale_file}")

def get_total_stars_used():
    total_stars = 0
    tracked_items = set()  # (item_name, price_bought_at, acquisition_method, stars_used)

    armory_dirs = ["armory_pass", "armory_pass/processed"]
    for armory_dir in armory_dirs:
        if os.path.exists(armory_dir):
            for filename in os.listdir(armory_dir):
                if filename.endswith(".csv"):
                    armory_file = os.path.join(armory_dir, filename)
                    with open(armory_file, "r", newline="", encoding="utf-8") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for armory_item in reader:
                            if armory_item["Acquisition Method"] == "Armory Pass":
                                key = (armory_item["Item Name"], float(armory_item["Price Bought At"]), 
                                       armory_item["Acquisition Method"], int(armory_item["Stars Used"]))
                                if key not in tracked_items:
                                    total_stars += int(armory_item["Stars Used"]) * int(armory_item["Count"])
                                    tracked_items.add(key)
    return total_stars

def get_total_revenue():
    total_revenue = 0

    sale_dirs = ["sales", "sales/processed"]
    for sale_dir in sale_dirs:
        if os.path.exists(sale_dir):
            for filename in os.listdir(sale_dir):
                if filename.endswith(".csv"):
                    sale_file = os.path.join(sale_dir, filename)
                    with open(sale_file, "r", newline="", encoding="utf-8") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for sale_item in reader:
                            total_revenue += float(sale_item["Sold Price"]) * int(sale_item["Count"])

    return total_revenue

def update_prices():
    # Get pass_price first
    pass_price = None
    armory_dirs = ["armory_pass", "armory_pass/processed"]
    for armory_dir in armory_dirs:
        if os.path.exists(armory_dir):
            for filename in os.listdir(armory_dir):
                if filename.endswith(".csv"):
                    with open(os.path.join(armory_dir, filename), "r", newline="", encoding="utf-8") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row["Acquisition Method"] == "One-Time Purchase":
                                pass_price = float(row["Price Bought At"])
                                break
                if pass_price:
                    break
        if pass_price:
            break

    if not pass_price:
        raise ValueError("CS2 Armory Pass price not found in armory_pass folder!")

    # Process all folders
    armory_dir = "armory_pass"
    if os.path.exists(armory_dir):
        for filename in os.listdir(armory_dir):
            if filename.endswith(".csv"):
                process_armory_pass(os.path.join(armory_dir, filename), pass_price)

    tradeup_dir = "tradeups"
    if os.path.exists(tradeup_dir):
        for filename in os.listdir(tradeup_dir):
            if filename.endswith(".csv"):
                process_tradeup(os.path.join(tradeup_dir, filename))

    case_dir = "case_openings"
    if os.path.exists(case_dir):
        for filename in os.listdir(case_dir):
            if filename.endswith(".csv"):
                process_case_opening(os.path.join(case_dir, filename))

    sales_dir = "sales"
    if os.path.exists(sales_dir):
        for filename in os.listdir(sales_dir):
            if filename.endswith(".csv"):
                process_sale(os.path.join(sales_dir, filename))

    # Load inventory
    items = []
    if not os.path.exists("inventory.csv"):
        with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = {
                "count": int(row["Count"]),
                "name": row["Item Name"],
                "price_bought_at": float(row["Price Bought At"]),
                "acquisition_method": row["Acquisition Method"]
            }
            items.append(item)

    # Update prices for inventory items
    results = []
    for item in items:
        current_price = clean_price(get_steam_price(item["name"]))
        if isinstance(current_price, float):
            net_price = current_price * 0.87  # After Steam fee
            effective_cost = item["price_bought_at"]
            profit_loss_per_item = round(net_price - effective_cost, 2)
            total_profit_loss = round(profit_loss_per_item * item["count"], 2)
        else:
            profit_loss_per_item = "N/A"
            total_profit_loss = "N/A"

        results.append({
            "Count": item["count"],
            "Item Name": item["name"],
            "Price Bought At": item["price_bought_at"],
            "Acquisition Method": item["acquisition_method"],
            "Current Steam Price": f"€{current_price:.2f}" if isinstance(current_price, float) else current_price,
            "Profit/Loss Per Item": profit_loss_per_item,
            "Total Profit/Loss": total_profit_loss,
            "Timestamp": datetime.now().isoformat()
        })
        time.sleep(3)

    with open("import requests
import time
import re

def get_steam_price(item_name):
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
                return data.get("lowest_price", "No Listings") if data.get("success") else "N/A"
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
        return 0.00", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method", 
                      "Current Steam Price", "Profit/Loss Per Item", "Total Profit/Loss", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    total_spent = sum(item["price_bought_at"] * item["count"] for item in items) + pass_price
    case_opening_count = 0
    case_dirs = ["case_openings", "case_openings/processed"]
    for case_dir in case_dirs:
        if os.path.exists(case_dir):
            case_opening_count += sum(1 for filename in os.listdir(case_dir) if filename.endswith(".csv"))
    total_spent += case_opening_count * 2.00  # €2 per key

    total_value = sum(clean_price(r["Current Steam Price"]) * r["Count"] * 0.87 
                      for r in results if isinstance(clean_price(r["Current Steam Price"]), float))
    total_stars_used = get_total_stars_used()
    total_revenue = get_total_revenue()

    profit_drops = profit_manual = profit_armory = profit_tradeups = profit_case_openings = 0
    for item in results:
        if item["Total Profit/Loss"] != "N/A":
            if item["Acquisition Method"] == "Game Drop":
                profit_drops += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Manual Purchase":
                profit_manual += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Armory Pass":
                profit_armory += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Trade-Up":
                profit_tradeups += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Case Opening":
                profit_case_openings += item["Total Profit/Loss"] - 2.00

    total_value = round(total_value, 2)
    profit_drops = round(profit_drops, 2)
    profit_manual = round(profit_manual, 2)
    profit_armory = round(profit_armory, 2)
    profit_tradeups = round(profit_tradeups, 2)
    profit_case_openings = round(profit_case_openings, 2)
    total_revenue = round(total_revenue, 2)

    print(f"\n--- Inventory Summary ---")
    print(f"Total Money Spent: €{total_spent:.2f}")
    print(f"Total Revenue from Sales: €{total_revenue:.2f}")
    print(f"Current Inventory Value (after fees): €{total_value:.2f}")
    print(f"Net Profit/Loss (including revenue): €{total_value + total_revenue - total_spent:.2f}")
    print(f"Total Stars Used: {total_stars_used} / 40")
    print(f"Profit from Drops: €{profit_drops:.2f}")
    print(f"Profit from Manual Purchases: €{profit_manual:.2f}")
    print(f"Profit from Armory Pass Items: €{profit_armory:.2f}")
    print(f"Profit from Trade-Ups: €{profit_tradeups:.2f}")
    print(f"Profit from Case Openings: €{profit_case_openings:.2f}")

if __name__ == "__main__":
    update_prices()