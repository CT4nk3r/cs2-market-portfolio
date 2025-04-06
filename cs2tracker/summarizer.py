import csv
import os
from datetime import datetime
from .price_fetcher import get_steam_price, clean_price
from .calculators import get_total_stars_used, get_total_revenue, calculate_tradeup_profit

def update_prices_and_summarize():
    pass_price = None
    armory_dirs = ["armory_pass", "armory_pass/processed"]  # Removed ../
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
        print("Warning: CS2 Armory Pass price not found. Using default €15.19 for calculations.")
        pass_price = 15.19

    items = []
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:  # Removed ../
        reader = csv.DictReader(csvfile)
        for row in reader:
            item = {
                "count": int(row["Count"]),
                "name": row["Item Name"],
                "price_bought_at": float(row["Price Bought At"]),
                "acquisition_method": row["Acquisition Method"]
            }
            items.append(item)

    results = []
    profitable_items = []
    for item in items:
        current_price = clean_price(get_steam_price(item["name"]))
        if isinstance(current_price, float):
            net_price = current_price * 0.87
            effective_cost = item["price_bought_at"]
            profit_loss_per_item = round(net_price - effective_cost, 2)
            total_profit_loss = round(profit_loss_per_item * item["count"], 2)
            if profit_loss_per_item > 0:
                profitable_items.append({
                    "Count": item["count"],
                    "Item Name": item["name"],
                    "Price Bought At": f"€{effective_cost:.2f}",
                    "Current Steam Price": f"€{current_price:.2f}",
                    "Net Sale Price": f"€{net_price:.2f}",
                    "Profit Per Item": f"€{profit_loss_per_item:.2f}",
                    "Total Profit": f"€{total_profit_loss:.2f}"
                })
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

    with open("prices.csv", "w", newline="", encoding="utf-8") as csvfile:  # Removed ../
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method", 
                      "Current Steam Price", "Profit/Loss Per Item", "Total Profit/Loss", "Timestamp"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    total_spent = sum(item["price_bought_at"] * item["count"] for item in items) + pass_price
    case_opening_count = 0
    case_dirs = ["case_openings", "case_openings/processed"]  # Removed ../
    for case_dir in case_dirs:
        if os.path.exists(case_dir):
            case_opening_count += sum(1 for filename in os.listdir(case_dir) if filename.endswith(".csv"))
    total_spent += case_opening_count * 2.00

    total_value = sum(clean_price(r["Current Steam Price"]) * r["Count"] * 0.87 
                      for r in results if isinstance(clean_price(r["Current Steam Price"]), float))
    total_stars_used = get_total_stars_used()
    total_revenue = get_total_revenue()
    profit_tradeups = calculate_tradeup_profit(items)

    profit_drops = profit_manual = profit_armory = profit_case_openings = 0
    for item in results:
        if item["Total Profit/Loss"] != "N/A":
            if item["Acquisition Method"] == "Game Drop":
                profit_drops += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Manual Purchase":
                profit_manual += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Armory Pass":
                profit_armory += item["Total Profit/Loss"]
            elif item["Acquisition Method"] == "Case Opening":
                profit_case_openings += item["Total Profit/Loss"] - 2.00

    total_value = round(total_value, 2)
    profit_drops = round(profit_drops, 2)
    profit_manual = round(profit_manual, 2)
    profit_armory = round(profit_armory, 2)
    profit_tradeups = round(profit_tradeups, 2)
    profit_case_openings = round(profit_case_openings, 2)
    total_revenue = round(total_revenue, 2)

    if profitable_items:
        print("\n--- Profitable Items to Sell ---")
        for item in profitable_items:
            print(f"{item['Count']}x {item['Item Name']}: "
                  f"Bought at {item['Price Bought At']}, "
                  f"Current {item['Current Steam Price']}, "
                  f"Net {item['Net Sale Price']}, "
                  f"Profit/Item {item['Profit Per Item']}, "
                  f"Total Profit {item['Total Profit']}")
    else:
        print("\n--- Profitable Items to Sell ---")
        print("No items are currently profitable to sell.")

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