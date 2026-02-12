"""
CDP Open Data Portal Downloader
Downloads corporate climate and emissions data from CDP
"""

import requests
import pandas as pd
from pathlib import Path
import time

BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data" / "cdp"

# CDP Socrata Open Data API
# Format: https://data.cdp.net/resource/{dataset_id}.csv

# Known CDP dataset IDs (found from portal exploration)
CDP_DATASETS = {
    # Corporate Climate Change datasets
    'kf4n-35ik': '2023_corporate_climate_change_responses',
    'b66y-bix2': '2022_corporate_climate_change_responses',
    'h3y5-etrb': '2021_corporate_climate_change_responses',
    'gyus-xmf5': '2020_corporate_climate_change_responses',

    # Corporate Scores
    'k48y-7dxq': '2023_corporate_scores',
    'nxwk-qi4z': '2022_corporate_scores',

    # City-Wide Emissions (for comparison/context)
    'p43t-fbkj': '2020_city_wide_emissions',

    # Supply Chain
    'yr9s-e3q2': '2022_supply_chain_climate',
}

def download_cdp_dataset(dataset_id, name, limit=50000):
    """Download a CDP dataset via Socrata API"""

    # Socrata API endpoint
    url = f"https://data.cdp.net/resource/{dataset_id}.csv?$limit={limit}"

    print(f"Downloading {name} ({dataset_id})...")

    try:
        response = requests.get(url, timeout=120)

        if response.status_code == 200:
            # Save CSV
            output_path = DATA_DIR / f"{name}.csv"
            with open(output_path, 'w') as f:
                f.write(response.text)

            # Check size
            df = pd.read_csv(output_path)
            print(f"  Saved: {output_path.name} ({len(df):,} rows, {len(df.columns)} columns)")

            # Show sample columns
            print(f"  Columns: {list(df.columns)[:5]}...")
            return df
        else:
            print(f"  Error: HTTP {response.status_code}")
            # Try to show error message
            if response.text:
                print(f"  Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"  Error: {e}")
        return None

def search_cdp_datasets(query="corporate"):
    """Search CDP catalog for datasets"""
    url = f"https://data.cdp.net/api/catalog/v1"
    params = {
        'q': query,
        'domains': 'data.cdp.net',
        'limit': 50,
        'only': 'datasets'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            datasets = []
            for r in data.get('results', []):
                res = r.get('resource', {})
                datasets.append({
                    'id': res.get('id'),
                    'name': res.get('name'),
                    'updated': res.get('updatedAt', '')[:10],
                    'type': res.get('type')
                })
            return datasets
    except Exception as e:
        print(f"Search error: {e}")
    return []

def main():
    """Download all known CDP corporate datasets"""
    print("="*60)
    print("CDP Open Data Portal Downloader")
    print("="*60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # First, search for available datasets
    print("\nSearching for corporate datasets...")
    datasets = search_cdp_datasets("corporate climate")

    if datasets:
        print(f"\nFound {len(datasets)} datasets:")
        for d in datasets[:10]:
            print(f"  {d['id']}: {d['name']} ({d['updated']})")

    # Download known datasets
    print("\n" + "="*60)
    print("Downloading known datasets...")
    print("="*60)

    downloaded = []
    for dataset_id, name in CDP_DATASETS.items():
        df = download_cdp_dataset(dataset_id, name)
        if df is not None:
            downloaded.append(name)
        time.sleep(1)  # Rate limiting

    print(f"\n\nSuccessfully downloaded: {len(downloaded)} datasets")
    print("Files saved to: data/cdp/")

    return downloaded

def quick_test():
    """Quick test with one dataset"""
    print("Testing CDP download...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Try 2020 city emissions (known to work)
    df = download_cdp_dataset('p43t-fbkj', 'test_2020_city_emissions', limit=1000)

    if df is not None:
        print("\nSample data:")
        print(df.head())
        return df
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        quick_test()
    else:
        main()
