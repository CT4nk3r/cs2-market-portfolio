import csv
import os

def process_armory_pass(armory_file, pass_price=None):
    if pass_price is None:
        with open(armory_file, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["Acquisition Method"] == "One-Time Purchase":
                    pass_price = float(row["Price Bought At"])
                    break
        if not pass_price:
            raise ValueError("Pass price not found in armory_pass file!")
    
    stars_per_euro = 40 / pass_price
    with open(armory_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        armory_items = list(reader)
    
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:  # Removed ../
        reader = csv.DictReader(csvfile)
        items = list(reader)
    
    for armory_item in armory_items:
        if armory_item["Acquisition Method"] != "One-Time Purchase":
            stars_used = int(armory_item["Stars Used"])
            price_in_euros = round(stars_used / stars_per_euro, 2)
            items.append({
                "Count": armory_item["Count"],
                "Item Name": armory_item["Item Name"],
                "Price Bought At": str(price_in_euros),
                "Acquisition Method": armory_item["Acquisition Method"]
            })
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:  # Removed ../
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    processed_dir = "armory_pass/processed"  # Removed ../
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(armory_file, f"{processed_dir}/{os.path.basename(armory_file)}")
    print(f"Processed armory pass: {armory_file}")

def process_tradeup(tradeup_file):
    with open(tradeup_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        tradeup_items = list(reader)
    
    output_item = next(item for item in tradeup_items if item["Acquisition Method"] == "Trade-Up")
    
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:  # Removed ../
        reader = csv.DictReader(csvfile)
        items = list(reader)
    
    items.append({
        "Count": output_item["Count"],
        "Item Name": output_item["Item Name"],
        "Price Bought At": output_item["Price Bought At"],
        "Acquisition Method": output_item["Acquisition Method"]
    })
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:  # Removed ../
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    processed_dir = "tradeups/processed"  # Removed ../
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(tradeup_file, f"{processed_dir}/{os.path.basename(tradeup_file)}")
    print(f"Processed trade-up: {tradeup_file}")

def process_case_opening(case_file):
    with open(case_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        case_data = next(reader)
    
    outcome_item = {"name": case_data["Outcome Item"]}
    
    with open("inventory.csv", "r", newline="", encoding="utf-8") as csvfile:  # Removed ../
        reader = csv.DictReader(csvfile)
        items = list(reader)
    
    items.append({
        "Count": "1",
        "Item Name": outcome_item["name"],
        "Price Bought At": "0.00",
        "Acquisition Method": "Case Opening"
    })
    
    with open("inventory.csv", "w", newline="", encoding="utf-8") as csvfile:  # Removed ../
        fieldnames = ["Count", "Item Name", "Price Bought At", "Acquisition Method"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(items)
    
    processed_dir = "case_openings/processed"  # Removed ../
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(case_file, f"{processed_dir}/{os.path.basename(case_file)}")
    print(f"Processed case opening: {case_file}")

def process_sale(sale_file):
    processed_dir = "sales/processed"  # Removed ../
    os.makedirs(processed_dir, exist_ok=True)
    os.rename(sale_file, f"{processed_dir}/{os.path.basename(sale_file)}")
    print(f"Processed sale: {sale_file}")