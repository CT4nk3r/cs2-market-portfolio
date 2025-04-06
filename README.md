# CS2 Market Portfolio

A Python tool to track profits from CS2 (Counter-Strike 2) items on the Steam Market. It processes inventory, armory passes, case openings, trade-ups, and sales, fetching current prices (with caching) to calculate profits and losses.

## Features
- Tracks items in `inventory.csv` and updates with current Steam Market prices.
- Processes transactions from `armory_pass/`, `case_openings/`, `tradeups/`, and `sales/` folders.
- Caches prices in `price_cache.json` (refreshes every 2 hours) to minimize API calls.
- Generates `prices.csv` with profit/loss details.
- Lists profitable items to sell.
- Runs daily via GitHub Actions, committing updates to the repo.

## Requirements
- **Python**: 3.x
- **Dependencies**: `requests` (`pip install requests`)
- **Files**: 
  - `inventory.csv` (initial inventory)
  - Optional: CSVs in `armory_pass/`, `case_openings/`, `tradeups/`, `sales/` folders

## Setup
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/<your-username>/cs2-market-portfolio.git
   cd cs2-market-portfolio
2. **Install Dependencies:**
    ```bash
    pip install requests
    ```
3. **Prepare Files:**
    - Ensure inventory.csv exists in the root:
        ```bash
        Count,Item Name,Price Bought At,Acquisition Method
        5,"Sticker | Boom Trail (Glitter)",0.00,"Game Drop"
        ```
    - Add transaction CSVs (optional) to armory_pass/, case_openings/, tradeups/, or sales/. Example armory_pass/armory_pass_20250405.csv:
        ```bash
        Count,Item Name,Price Bought At,Acquisition Method,Stars Used
        1,"CS2 Armory Pass",15.19,"One-Time Purchase",0
        ```
## Usage
Run from the root directory (cs2-market-portfolio/):
### Update Prices and Summary:
```bash
python -m cs2tracker.CS2ProfitMaster
```
- Processes new CSVs, fetches prices, updates inventory.csv, and writes prices.csv.
- Outputs a summary with total spent, revenue, and profits by category.
### Analyze Profitable Items:
    ```bash 
    python -m cs2tracker.ProfitAnalyzer
    ```
        - Reads prices.csv and lists items you can sell for a profit.
## File Structure
```
cs2-market-portfolio/
├── cs2tracker/              # Python package
│   ├── CS2ProfitMaster.py  # Main script
│   ├── price_fetcher.py    # Steam API and price cleaning
│   ├── processors.py       # Processes transaction CSVs
│   ├── calculators.py      # Computes profits and stats
│   ├── summarizer.py       # Generates summary and prices.csv
│   ├── ProfitAnalyzer.py   # Lists profitable items
│   ├── price_cache.py      # Manages price caching
│   └── __init__.py
├── inventory.csv           # Current inventory
├── armory_pass/            # Armory pass transactions
├── case_openings/          # Case opening records
├── tradeups/               # Trade-up records
├── sales/                  # Sale records
├── prices.csv              # Generated price data
├── price_cache.json        # Cached Steam prices
└── .github/workflows/      # GitHub Actions config
    └── daily-profit-run.yml
```
- Processed Subfolders: Each data folder has a processed/ subfolder where processed CSVs are moved (e.g., armory_pass/processed/).

## GitHub Actions
- Workflow: daily-profit-run.yml
- Schedule: Runs daily at midnight UTC (0 0 * * *).
- Actions:
    - Checks out the repo.
    - Sets up Python and installs requests.
    - Runs python -m cs2tracker.CS2ProfitMaster.
    - Commits and pushes updates to prices.csv and price_cache.json.
- Manual Trigger: Use the "Run workflow" button in the GitHub Actions tab.

## Notes
- Price Caching: Prices refresh every 2 hours to avoid Steam API rate limits.
- Armory Pass: If no pass price is found in armory_pass/ CSVs, it defaults to €15.19.
- Troubleshooting: Ensure CSVs are in the root folders (not just processed/ subdirs) for initial processing.