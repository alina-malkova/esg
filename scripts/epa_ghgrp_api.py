"""
EPA GHGRP Data Download via Envirofacts API
Downloads facility-level greenhouse gas emissions data
"""

import requests
import pandas as pd
from pathlib import Path
import time

BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data" / "epa_ghgrp"

# Envirofacts REST API
# Documentation: https://www.epa.gov/enviro/envirofacts-data-service-api

def download_ghgrp_data(table_name, rows=10000, start=0):
    """Download data from EPA Envirofacts API"""
    # API endpoint format: https://data.epa.gov/efservice/{table}/JSON
    # or CSV: https://data.epa.gov/efservice/{table}/rows/{start}:{end}/CSV

    base_url = f"https://data.epa.gov/efservice/{table_name}"

    try:
        # Get row count first
        count_url = f"{base_url}/count/JSON"
        response = requests.get(count_url, timeout=30)
        if response.status_code == 200:
            count_data = response.json()
            total_rows = count_data[0].get('TOTALQUERYRESULTS', 0) if count_data else 0
            print(f"Table {table_name}: {total_rows:,} total rows")
        else:
            total_rows = None
            print(f"Could not get count for {table_name}")

        # Download data
        data_url = f"{base_url}/rows/{start}:{start + rows}/CSV"
        print(f"Downloading from: {data_url}")

        response = requests.get(data_url, timeout=120)
        response.raise_for_status()

        return response.text, total_rows

    except Exception as e:
        print(f"Error downloading {table_name}: {e}")
        return None, None

def download_all_ghgrp_tables():
    """Download key GHGRP tables"""
    print("="*60)
    print("EPA GHGRP Data Download via Envirofacts API")
    print("="*60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Key GHGRP tables
    # See: https://enviro.epa.gov/envirofacts/ghg/model
    tables = {
        'V_GHG_EMITTER_FACILITIES': 'ghgrp_facilities.csv',      # Facility info
        'V_GHG_EMITTER_GHG': 'ghgrp_emissions.csv',              # Emissions by facility
        'V_GHG_EMITTER_SUBPART': 'ghgrp_subparts.csv',           # Subpart details
    }

    for table, filename in tables.items():
        print(f"\n--- Downloading {table} ---")
        csv_data, total = download_ghgrp_data(table, rows=50000)

        if csv_data:
            output_path = DATA_DIR / filename
            with open(output_path, 'w') as f:
                f.write(csv_data)

            # Verify
            df = pd.read_csv(output_path)
            print(f"Saved: {output_path} ({len(df):,} rows, {len(df.columns)} columns)")
            print(f"Columns: {list(df.columns)[:5]}...")

        time.sleep(1)

def quick_test():
    """Test API with a small sample"""
    print("Testing EPA Envirofacts API...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Test with facility data
    csv_data, total = download_ghgrp_data('V_GHG_EMITTER_FACILITIES', rows=1000)

    if csv_data:
        output_path = DATA_DIR / "ghgrp_facilities_sample.csv"
        with open(output_path, 'w') as f:
            f.write(csv_data)

        df = pd.read_csv(output_path)
        print(f"\nSaved: {output_path}")
        print(f"Rows: {len(df):,}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nSample data:")
        print(df.head())
        return df

    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        download_all_ghgrp_tables()
    else:
        quick_test()
