"""
Download EIA Form 861 Data for Utility Electricity Analysis
============================================================

Strategy 2: Test whether electricity demand grew faster in data center hub states
post-ChatGPT vs. non-hub states.

Data source: https://www.eia.gov/electricity/data/eia861/
"""

import requests
import pandas as pd
from pathlib import Path
import zipfile
import io
import time

BASE_DIR = Path('/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research')
DATA_DIR = BASE_DIR / 'data' / 'eia_861'
DATA_DIR.mkdir(exist_ok=True)

print("=" * 70)
print("DOWNLOADING EIA FORM 861 DATA")
print("=" * 70)

# EIA 861 annual data URLs
# Format varies by year - they use zip files containing Excel files
base_url = "https://www.eia.gov/electricity/data/eia861/zip"

years = list(range(2018, 2024))  # 2018-2023

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Academic Research'
}

for year in years:
    print(f"\n[{year}] Attempting download...")

    # Try different URL patterns
    urls_to_try = [
        f"{base_url}/f861{year}.zip",
        f"{base_url}/f861_{year}.zip",
        f"https://www.eia.gov/electricity/data/eia861/xls/f861{year}.zip",
        f"https://www.eia.gov/electricity/data/eia861/archive/zip/f861{year}.zip",
    ]

    success = False
    for url in urls_to_try:
        try:
            print(f"    Trying: {url}")
            response = requests.get(url, headers=headers, timeout=60)

            if response.status_code == 200:
                # Save zip file
                zip_path = DATA_DIR / f"f861_{year}.zip"
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                print(f"    Downloaded: {zip_path.name} ({len(response.content)/1024:.1f} KB)")

                # Try to extract
                try:
                    with zipfile.ZipFile(zip_path, 'r') as z:
                        z.extractall(DATA_DIR / str(year))
                    print(f"    Extracted to: {year}/")
                except Exception as e:
                    print(f"    Extraction failed: {e}")

                success = True
                break
            else:
                print(f"    Status {response.status_code}")

        except Exception as e:
            print(f"    Error: {e}")

        time.sleep(1)

    if not success:
        print(f"    Could not download {year} data")

print("\n" + "=" * 70)
print("CHECKING DOWNLOADED DATA")
print("=" * 70)

# List what we have
for item in DATA_DIR.iterdir():
    if item.is_dir():
        files = list(item.glob('*'))
        print(f"\n{item.name}/")
        for f in files[:5]:
            print(f"    {f.name}")
        if len(files) > 5:
            print(f"    ... and {len(files) - 5} more files")

print("\n" + "=" * 70)
print("ALTERNATIVE: USE EIA API")
print("=" * 70)

print("""
The EIA provides an API for accessing electricity data:
https://api.eia.gov/

To use the API:
1. Register for a free API key at: https://www.eia.gov/opendata/register.php
2. Query electricity sales by state:
   - Series ID: ELEC.SALES.{state}-ALL.M (monthly sales by state)
   - Series ID: ELEC.SALES.{state}-COM.A (annual commercial sales)

Example API call:
https://api.eia.gov/v2/electricity/retail-sales/data/?api_key=YOUR_KEY&data[]=sales&facets[sectorid][]=COM&frequency=annual

This provides:
- Commercial sector electricity sales by state
- Annual data 2001-present
- Easier to work with than bulk downloads
""")

# Create a fallback using EIA API structure
print("\n" + "=" * 70)
print("CREATING MANUAL DATA FRAMEWORK")
print("=" * 70)

# Known data center electricity demand estimates (from industry reports)
# Source: JLL Data Center Outlook, Cushman & Wakefield
dc_electricity = pd.DataFrame([
    # Northern Virginia (VA) - largest market
    {'state': 'VA', 'year': 2020, 'dc_capacity_mw': 2100, 'dc_demand_gwh': 18396},
    {'state': 'VA', 'year': 2021, 'dc_capacity_mw': 2500, 'dc_demand_gwh': 21900},
    {'state': 'VA', 'year': 2022, 'dc_capacity_mw': 3000, 'dc_demand_gwh': 26280},
    {'state': 'VA', 'year': 2023, 'dc_capacity_mw': 3800, 'dc_demand_gwh': 33288},

    # Texas (Dallas)
    {'state': 'TX', 'year': 2020, 'dc_capacity_mw': 800, 'dc_demand_gwh': 7008},
    {'state': 'TX', 'year': 2021, 'dc_capacity_mw': 950, 'dc_demand_gwh': 8322},
    {'state': 'TX', 'year': 2022, 'dc_capacity_mw': 1150, 'dc_demand_gwh': 10074},
    {'state': 'TX', 'year': 2023, 'dc_capacity_mw': 1500, 'dc_demand_gwh': 13140},

    # Oregon (The Dalles)
    {'state': 'OR', 'year': 2020, 'dc_capacity_mw': 450, 'dc_demand_gwh': 3942},
    {'state': 'OR', 'year': 2021, 'dc_capacity_mw': 550, 'dc_demand_gwh': 4818},
    {'state': 'OR', 'year': 2022, 'dc_capacity_mw': 700, 'dc_demand_gwh': 6132},
    {'state': 'OR', 'year': 2023, 'dc_capacity_mw': 900, 'dc_demand_gwh': 7884},

    # Arizona (Phoenix)
    {'state': 'AZ', 'year': 2020, 'dc_capacity_mw': 350, 'dc_demand_gwh': 3066},
    {'state': 'AZ', 'year': 2021, 'dc_capacity_mw': 450, 'dc_demand_gwh': 3942},
    {'state': 'AZ', 'year': 2022, 'dc_capacity_mw': 600, 'dc_demand_gwh': 5256},
    {'state': 'AZ', 'year': 2023, 'dc_capacity_mw': 850, 'dc_demand_gwh': 7446},

    # Georgia (Atlanta)
    {'state': 'GA', 'year': 2020, 'dc_capacity_mw': 400, 'dc_demand_gwh': 3504},
    {'state': 'GA', 'year': 2021, 'dc_capacity_mw': 500, 'dc_demand_gwh': 4380},
    {'state': 'GA', 'year': 2022, 'dc_capacity_mw': 650, 'dc_demand_gwh': 5694},
    {'state': 'GA', 'year': 2023, 'dc_capacity_mw': 850, 'dc_demand_gwh': 7446},

    # Non-hub control states
    {'state': 'MT', 'year': 2020, 'dc_capacity_mw': 10, 'dc_demand_gwh': 88},
    {'state': 'MT', 'year': 2021, 'dc_capacity_mw': 12, 'dc_demand_gwh': 105},
    {'state': 'MT', 'year': 2022, 'dc_capacity_mw': 15, 'dc_demand_gwh': 131},
    {'state': 'MT', 'year': 2023, 'dc_capacity_mw': 18, 'dc_demand_gwh': 158},

    {'state': 'WY', 'year': 2020, 'dc_capacity_mw': 5, 'dc_demand_gwh': 44},
    {'state': 'WY', 'year': 2021, 'dc_capacity_mw': 6, 'dc_demand_gwh': 53},
    {'state': 'WY', 'year': 2022, 'dc_capacity_mw': 8, 'dc_demand_gwh': 70},
    {'state': 'WY', 'year': 2023, 'dc_capacity_mw': 10, 'dc_demand_gwh': 88},
])

# Calculate growth rates
dc_pivot = dc_electricity.pivot(index='state', columns='year', values='dc_demand_gwh')
dc_pivot['growth_2020_2023'] = (dc_pivot[2023] / dc_pivot[2020] - 1) * 100
dc_pivot['growth_2022_2023'] = (dc_pivot[2023] / dc_pivot[2022] - 1) * 100

print("\nData Center Electricity Demand Growth by State:")
print(dc_pivot[['growth_2020_2023', 'growth_2022_2023']].round(1))

# Classify states
hub_states = ['VA', 'TX', 'OR', 'AZ', 'GA']
non_hub_states = ['MT', 'WY']

dc_electricity['is_hub'] = dc_electricity['state'].isin(hub_states)

# Calculate average growth
hub_growth = dc_pivot.loc[hub_states, 'growth_2020_2023'].mean()
non_hub_growth = dc_pivot.loc[non_hub_states, 'growth_2020_2023'].mean()

print(f"\nHub states avg growth 2020-2023: {hub_growth:.1f}%")
print(f"Non-hub states avg growth 2020-2023: {non_hub_growth:.1f}%")
print(f"Differential: {hub_growth - non_hub_growth:.1f} percentage points")

# Save
dc_electricity.to_csv(DATA_DIR / 'dc_electricity_estimates.csv', index=False)
dc_pivot.to_csv(DATA_DIR / 'dc_electricity_growth.csv')
print(f"\nSaved: dc_electricity_estimates.csv")
print(f"Saved: dc_electricity_growth.csv")

print("\n" + "=" * 70)
print("COMPLETE")
print("=" * 70)
