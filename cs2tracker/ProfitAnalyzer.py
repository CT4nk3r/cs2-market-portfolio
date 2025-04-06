import csv
import os
from datetime import datetime

def analyze_prices():
    if not os.path.exists("prices.csv"):  # Removed ../
        print("Error: prices.csv not found. Run CS2ProfitMaster first.")
        return

    profitable_items = []
    with open("prices.csv", "r", newline="", encoding="utf-8") as csvfile:  # Removed ../
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                price_bought_at = float(row["Price Bought At"])
                current_price = row["Current Steam Price"].replace("€", "")
                profit_per_item = float(row["Profit/Loss Per Item"])
                total_profit = float(row["Total Profit/Loss"])
                count = int(row["Count"])
                if profit_per_item > 0:
                    profitable_items.append({
                        "Count": count,
                        "Item Name": row["Item Name"],
                        "Price Bought At": f"€{price_bought_at:.2f}",
                        "Current Steam Price": f"€{current_price}",
                        "Net Sale Price": f"€{(float(current_price) * 0.87):.2f}",
                        "Profit Per Item": f"€{profit_per_item:.2f}",
                        "Total Profit": f"€{total_profit:.2f}"
                    })
            except (ValueError, KeyError):
                continue

    if profitable_items:
        print("\n--- Profitable Items to Sell (from prices.csv) ---")
        for item in profitable_items:
            print(f"{item['Count']}x {item['Item Name']}: "
                  f"Bought at {item['Price Bought At']}, "
                  f"Current {item['Current Steam Price']}, "
                  f"Net {item['Net Sale Price']}, "
                  f"Profit/Item {item['Profit Per Item']}, "
                  f"Total Profit {item['Total Profit']}")
    else:
        print("\n--- Profitable Items to Sell (from prices.csv) ---")
        print("No items are currently profitable to sell.")

if __name__ == "__main__":
    analyze_prices()