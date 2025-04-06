import csv
import os
from .price_fetcher import get_steam_price, clean_price

def get_total_stars_used():
    total_stars = 0
    tracked_items = set()

    armory_dirs = ["armory_pass", "armory_pass/processed"]  # Removed ../
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

    sale_dirs = ["sales", "sales/processed"]  # Removed ../
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

def calculate_tradeup_profit(inventory_items):
    profit_tradeups = 0
    tradeup_dirs = ["tradeups", "tradeups/processed"]  # Removed ../
    sale_dirs = ["sales", "sales/processed"]  # Removed ../
    sold_items = {}
    for sale_dir in sale_dirs:
        if os.path.exists(sale_dir):
            for filename in os.listdir(sale_dir):
                if filename.endswith(".csv"):
                    with open(os.path.join(sale_dir, filename), "r", newline="", encoding="utf-8") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for sale_item in reader:
                            sold_items[sale_item["Item Name"]] = float(sale_item["Sold Price"]) * 0.87

    inventory_dict = {item["name"]: item["price_bought_at"] for item in inventory_items}

    for tradeup_dir in tradeup_dirs:
        if os.path.exists(tradeup_dir):
            for filename in os.listdir(tradeup_dir):
                if filename.endswith(".csv"):
                    tradeup_file = os.path.join(tradeup_dir, filename)
                    with open(tradeup_file, "r", newline="", encoding="utf-8") as csvfile:
                        reader = csv.DictReader(csvfile)
                        tradeup_items = list(reader)
                        inputs = [item for item in tradeup_items if item["Acquisition Method"] != "Trade-Up"]
                        output = next(item for item in tradeup_items if item["Acquisition Method"] == "Trade-Up")
                        
                        input_cost = 0
                        for input_item in inputs:
                            if input_item["Item Name"] in inventory_dict:
                                input_cost += inventory_dict[input_item["Item Name"]] * int(input_item["Count"])
                            else:
                                print(f"Warning: Input {input_item['Item Name']} not found in inventory for cost calculation")

                        if output["Item Name"] in sold_items:
                            output_revenue = sold_items[output["Item Name"]] * int(output["Count"])
                        else:
                            current_price = clean_price(get_steam_price(output["Item Name"]))
                            if isinstance(current_price, float):
                                output_revenue = current_price * 0.87 * int(output["Count"])
                            else:
                                output_revenue = 0.00
                        
                        profit_tradeups += (output_revenue - input_cost)
    
    return profit_tradeups