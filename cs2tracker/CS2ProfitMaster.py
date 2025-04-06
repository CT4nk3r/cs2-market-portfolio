import os
import csv
from .processors import process_armory_pass, process_tradeup, process_case_opening, process_sale
from .calculators import get_total_stars_used, get_total_revenue, calculate_tradeup_profit
from .summarizer import update_prices_and_summarize

def main():
    print("Checking inventory.csv...")
    if not os.path.exists("inventory.csv"):  # Removed ../
        print("inventory.csv not found, creating it.")
        with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
    else:
        print("inventory.csv found.")

    for folder, processor in [
        ("armory_pass", process_armory_pass),  # Removed ../
        ("tradeups", process_tradeup),
        ("case_openings", process_case_opening),
        ("sales", process_sale)
    ]:
        print(f"Checking folder: {folder}")
        if os.path.exists(folder):
            csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
            print(f"Found {len(csv_files)} CSV files in {folder}: {csv_files}")
            for filename in csv_files:
                full_path = os.path.join(folder, filename)
                processor(full_path)
        else:
            print(f"Folder {folder} does not exist.")

    update_prices_and_summarize()

if __name__ == "__main__":
    main()