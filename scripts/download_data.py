"""
Download research data for AI-ESG trade-off study
"""

import os
import requests
import pandas as pd
from pathlib import Path
import zipfile
import io

# Base paths
BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data"

def download_file(url, filepath, headers=None):
    """Download file with proper redirect handling"""
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    try:
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=60)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filepath} ({len(response.content):,} bytes)")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def download_patentsview():
    """Download PatentsView data for AI patent identification"""
    print("\n=== Downloading PatentsView Data ===")
    patents_dir = DATA_DIR / "patents"

    # PatentsView bulk data URLs (2024 version)
    urls = {
        'g_cpc_current.tsv.zip': 'https://s3.amazonaws.com/data.patentsview.org/pregrant_publications/pg_cpc_at_issue.tsv.zip',
    }

    # Note: Main patent files are very large (>10GB). We'll download CPC codes and provide instructions
    print("Note: Full patent files are very large. Creating download instructions...")

    instructions = """
PatentsView Bulk Data Download Instructions
==========================================

The full PatentsView dataset is very large (>10GB). Download manually from:
https://patentsview.org/download/data-download-tables

Key files needed:
1. g_patent.tsv.zip - Main patent data (~3GB compressed)
2. g_cpc_current.tsv.zip - CPC classifications for AI filtering
3. g_assignee.tsv.zip - Assignee/company information

AI-related CPC codes to filter:
- G06N (Machine learning, neural networks)
- G06F 18/ (Pattern recognition)
- G06F 40/ (Natural language processing)
- G10L (Speech recognition)
- G06V (Image recognition)
- G06Q (Business AI applications)

Alternative: Use PatentsView API for targeted queries:
https://api.patentsview.org/
"""
    with open(patents_dir / "DOWNLOAD_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    print(f"Created: {patents_dir / 'DOWNLOAD_INSTRUCTIONS.txt'}")

def download_epa_egrid():
    """Download EPA eGRID data - already downloaded"""
    print("\n=== EPA eGRID ===")
    egrid_file = DATA_DIR / "epa_egrid" / "eGRID2022_data.xlsx"
    if egrid_file.exists() and egrid_file.stat().st_size > 1000000:
        print(f"Already downloaded: {egrid_file} ({egrid_file.stat().st_size:,} bytes)")
    else:
        print("eGRID needs manual download from: https://www.epa.gov/egrid/download-data")

def download_ghgrp():
    """Download EPA GHGRP facility emissions data"""
    print("\n=== Downloading EPA GHGRP Data ===")
    ghgrp_dir = DATA_DIR / "epa_ghgrp"

    # Try direct flight tool export URL
    # The data is best accessed through EPA's Envirofacts or FLIGHT tool
    instructions = """
EPA GHGRP Data Download Instructions
=====================================

Facility-level emissions data requires interactive download:

Option 1: Envirofacts (Recommended for bulk data)
- URL: https://enviro.epa.gov/envirofacts/ghg/search
- Select all years, export to CSV
- Covers all facilities reporting under GHGRP

Option 2: FLIGHT Tool (Interactive mapping)
- URL: https://ghgdata.epa.gov/ghgp/main.do
- Good for exploring specific facilities/regions

Option 3: Pre-packaged Data Summaries
- URL: https://www.epa.gov/ghgreporting/data-sets
- "Data Summary Spreadsheets" contains yearly facility data

Key fields:
- Facility ID, Name, Address, Parent Company
- Total reported emissions (CO2e)
- Industry type (NAICS code)
- Sector-specific breakdowns
"""
    with open(ghgrp_dir / "DOWNLOAD_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    print(f"Created: {ghgrp_dir / 'DOWNLOAD_INSTRUCTIONS.txt'}")

def download_fred_data():
    """Download macroeconomic data from FRED"""
    print("\n=== Downloading FRED Data ===")
    from pandas_datareader import data as pdr

    fred_dir = DATA_DIR / "fred"
    fred_dir.mkdir(exist_ok=True)

    # Key macro indicators
    series = {
        'GDP': 'GDP',
        'UNRATE': 'UNRATE',  # Unemployment rate
        'CPIAUCSL': 'CPIAUCSL',  # CPI
        'FEDFUNDS': 'FEDFUNDS',  # Fed funds rate
        'SP500': 'SP500',  # S&P 500
        'INDPRO': 'INDPRO',  # Industrial production
    }

    try:
        for name, code in series.items():
            df = pdr.DataReader(code, 'fred', start='2015-01-01')
            df.to_csv(fred_dir / f"{name}.csv")
            print(f"Downloaded: {name}.csv")
    except Exception as e:
        print(f"FRED download error: {e}")
        print("Note: Some FRED series may require API key")

def download_sp500_list():
    """Download S&P 500 constituent list"""
    print("\n=== Downloading S&P 500 List ===")

    try:
        # Wikipedia table of S&P 500 companies
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        sp500 = tables[0]
        sp500.to_csv(DATA_DIR / "sp500_constituents.csv", index=False)
        print(f"Downloaded: sp500_constituents.csv ({len(sp500)} companies)")
    except Exception as e:
        print(f"S&P 500 list download error: {e}")

def download_stock_data():
    """Download stock data for sample firms using yfinance"""
    print("\n=== Downloading Sample Stock Data ===")
    import yfinance as yf

    stocks_dir = DATA_DIR / "stocks"
    stocks_dir.mkdir(exist_ok=True)

    # Major tech firms for initial analysis
    tech_tickers = ['GOOGL', 'MSFT', 'META', 'AMZN', 'AAPL', 'NVDA', 'AMD', 'INTC']

    for ticker in tech_tickers:
        try:
            stock = yf.Ticker(ticker)
            # Historical prices
            hist = stock.history(start="2018-01-01")
            hist.to_csv(stocks_dir / f"{ticker}_prices.csv")

            # Basic info
            info = stock.info
            pd.DataFrame([info]).to_csv(stocks_dir / f"{ticker}_info.csv", index=False)
            print(f"Downloaded: {ticker}")
        except Exception as e:
            print(f"Error downloading {ticker}: {e}")

def create_ai_exposure_data():
    """Create AI exposure index based on Felten et al. methodology"""
    print("\n=== Creating AI Exposure Index ===")

    ai_dir = DATA_DIR / "ai_exposure"

    # Create methodology notes and manual download instructions
    methodology = """
AI Occupational Exposure Index
==============================

Based on Felten, Raj, and Seamans (2021) methodology.

Data Sources (all free):
1. O*NET Database: https://www.onetcenter.org/database.html
   - Download: "Abilities" and "Work Activities" files

2. BLS OES Data: https://www.bls.gov/oes/tables.htm
   - Industry-occupation employment matrices

3. AI Application Mapping:
   The Felten et al. approach maps AI capabilities to O*NET abilities.
   Their scores are available at: https://osf.io/3a5n2/

Construction Steps:
1. Map AI applications to cognitive abilities in O*NET
2. Calculate ability-level AI exposure scores
3. Aggregate to occupation level using ability importance weights
4. Aggregate to industry level using employment shares

Key Reference:
Felten, E., Raj, M., & Seamans, R. (2021). "Occupational, industry,
and geographic exposure to artificial intelligence: A novel dataset
and its potential uses." Strategic Management Journal.
"""
    with open(ai_dir / "METHODOLOGY.txt", "w") as f:
        f.write(methodology)
    print(f"Created: {ai_dir / 'METHODOLOGY.txt'}")

    # Download O*NET data
    try:
        # O*NET abilities data
        abilities_url = "https://www.onetcenter.org/dl_files/database/db_28_3_text/Abilities.txt"
        download_file(abilities_url, ai_dir / "onet_abilities.txt")
    except Exception as e:
        print(f"O*NET download error: {e}")

def main():
    """Run all downloads"""
    print("="*60)
    print("AI-ESG Research Data Download Script")
    print("="*60)

    # Create directories
    for subdir in ['patents', 'epa_egrid', 'epa_ghgrp', 'ai_exposure', 'ken_french',
                   'sec_filings', 'fred', 'stocks']:
        (DATA_DIR / subdir).mkdir(parents=True, exist_ok=True)

    # Run downloads
    download_patentsview()
    download_epa_egrid()
    download_ghgrp()
    download_fred_data()
    download_sp500_list()
    download_stock_data()
    create_ai_exposure_data()

    print("\n" + "="*60)
    print("Download Summary")
    print("="*60)

    # List all downloaded files
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            filepath = Path(root) / file
            print(f"  {filepath.relative_to(DATA_DIR)}: {filepath.stat().st_size:,} bytes")

if __name__ == "__main__":
    main()
