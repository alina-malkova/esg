"""
EPA GHGRP Data Processor
Processes facility-level emissions and matches to S&P 500 firms

INSTRUCTIONS:
1. Download EPA GHGRP data from: https://www.epa.gov/ghgreporting/data-sets
2. Download "Data Summary Spreadsheets" for each year (2015-2023)
3. Extract ZIP files to: data/epa_ghgrp/raw/
4. Run this script: python scripts/process_epa_ghgrp.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from fuzzywuzzy import fuzz, process
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data" / "epa_ghgrp"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_DIR = DATA_DIR / "processed"

def clean_company_name(name):
    """Standardize company names for matching"""
    if pd.isna(name):
        return ""

    name = str(name).upper().strip()

    # Remove common suffixes
    suffixes = [
        r'\s+INC\.?$', r'\s+INCORPORATED$', r'\s+CORP\.?$', r'\s+CORPORATION$',
        r'\s+LLC$', r'\s+L\.L\.C\.?$', r'\s+LTD\.?$', r'\s+LIMITED$',
        r'\s+CO\.?$', r'\s+COMPANY$', r'\s+LP$', r'\s+L\.P\.?$',
        r'\s+PLC$', r'\s+NA$', r'\s+USA$', r'\s+US$', r'\s+AMERICAS?$',
        r'\s+HOLDINGS?$', r'\s+GROUP$', r'\s+ENTERPRISES?$',
        r',.*$',  # Remove everything after comma
    ]

    for suffix in suffixes:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)

    # Remove special characters
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name

def load_sp500_companies():
    """Load S&P 500 company list"""
    sp500_file = BASE_DIR / "data" / "sp500_constituents.csv"

    if not sp500_file.exists():
        print("ERROR: S&P 500 file not found. Run download_data.py first.")
        return None

    df = pd.read_csv(sp500_file)
    df['clean_name'] = df['Security'].apply(clean_company_name)
    df['ticker'] = df['Symbol']

    # Create name variations for matching
    name_to_ticker = {}
    for _, row in df.iterrows():
        name_to_ticker[row['clean_name']] = row['ticker']
        # Also add ticker as possible match
        name_to_ticker[row['ticker']] = row['ticker']

    return df, name_to_ticker

def find_ghgrp_files():
    """Find all GHGRP data files in raw directory"""
    if not RAW_DIR.exists():
        print(f"Creating raw data directory: {RAW_DIR}")
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        return []

    # Look for Excel files with emissions data
    patterns = ['*.xlsx', '*.xls', '*.csv']
    files = []
    for pattern in patterns:
        files.extend(RAW_DIR.glob(pattern))
        files.extend(RAW_DIR.glob(f'**/{pattern}'))

    return sorted(files)

def read_ghgrp_file(filepath):
    """Read a single GHGRP data file"""
    print(f"  Reading: {filepath.name}")

    try:
        if filepath.suffix.lower() in ['.xlsx', '.xls']:
            # Try different sheet names
            xl = pd.ExcelFile(filepath)
            sheet_names = xl.sheet_names

            # Look for the main data sheet
            target_sheets = [s for s in sheet_names if any(
                kw in s.lower() for kw in ['direct', 'emission', 'facility', 'data', 'ghg']
            )]

            if target_sheets:
                df = pd.read_excel(filepath, sheet_name=target_sheets[0])
            else:
                df = pd.read_excel(filepath, sheet_name=0)
        else:
            df = pd.read_csv(filepath)

        return df

    except Exception as e:
        print(f"    Error reading {filepath.name}: {e}")
        return None

def standardize_columns(df):
    """Standardize column names across different file formats"""
    # Create lowercase column mapping
    col_map = {col: col.lower().strip().replace(' ', '_') for col in df.columns}
    df = df.rename(columns=col_map)

    # Common column name variations
    renames = {
        # Facility info
        'facility_name': ['facility_name', 'facility', 'name'],
        'facility_id': ['facility_id', 'ghgrp_id', 'epa_facility_id', 'facid'],
        'parent_company': ['parent_companies', 'parent_company', 'parent_co', 'reporting_company'],
        'state': ['state', 'facility_state', 'st'],
        'city': ['city', 'facility_city'],
        'zip': ['zip', 'zip_code', 'zipcode'],
        'latitude': ['latitude', 'lat'],
        'longitude': ['longitude', 'lon', 'long'],

        # Emissions
        'total_emissions': ['total_reported_direct_emissions', 'total_direct_emissions',
                          'ghg_quantity', 'total_emissions', 'co2e_emissions',
                          'total_reported_emissions'],

        # Industry
        'naics_code': ['primary_naics_code', 'naics_code', 'naics', 'industry_code'],
        'industry': ['industry_type', 'industry_sector', 'sector'],

        # Year
        'year': ['reporting_year', 'year', 'data_year', 'fiscal_year'],
    }

    for standard_name, variations in renames.items():
        for var in variations:
            if var in df.columns and standard_name not in df.columns:
                df = df.rename(columns={var: standard_name})
                break

    return df

def match_to_sp500(ghgrp_df, name_to_ticker, sp500_names):
    """Match GHGRP parent companies to S&P 500 tickers using fuzzy matching"""
    print("  Matching companies to S&P 500...")

    if 'parent_company' not in ghgrp_df.columns:
        print("    WARNING: No parent_company column found")
        return ghgrp_df

    # Clean parent company names
    ghgrp_df['clean_parent'] = ghgrp_df['parent_company'].apply(clean_company_name)

    # Direct matching first
    ghgrp_df['ticker'] = ghgrp_df['clean_parent'].map(name_to_ticker)

    # Fuzzy matching for unmatched
    unmatched = ghgrp_df[ghgrp_df['ticker'].isna()]['clean_parent'].unique()
    print(f"    Direct matches: {ghgrp_df['ticker'].notna().sum():,}")
    print(f"    Attempting fuzzy match for {len(unmatched):,} unique companies...")

    fuzzy_matches = {}
    for name in unmatched:
        if not name or len(name) < 3:
            continue

        # Find best match
        match = process.extractOne(name, sp500_names, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 80:  # 80% similarity threshold
            fuzzy_matches[name] = name_to_ticker.get(match[0])

    # Apply fuzzy matches
    ghgrp_df['ticker'] = ghgrp_df.apply(
        lambda row: row['ticker'] if pd.notna(row['ticker'])
                    else fuzzy_matches.get(row['clean_parent']),
        axis=1
    )

    matched = ghgrp_df['ticker'].notna().sum()
    print(f"    Total matched: {matched:,} ({matched/len(ghgrp_df)*100:.1f}%)")

    return ghgrp_df

def aggregate_by_company_year(df):
    """Aggregate facility emissions to company-year level"""
    if 'ticker' not in df.columns or 'year' not in df.columns:
        return df

    # Only keep matched firms
    matched_df = df[df['ticker'].notna()].copy()

    if len(matched_df) == 0:
        return pd.DataFrame()

    # Aggregation
    agg_dict = {
        'total_emissions': 'sum',
        'facility_id': 'count',  # Number of facilities
    }

    # Only aggregate columns that exist
    agg_dict = {k: v for k, v in agg_dict.items() if k in matched_df.columns}

    if not agg_dict:
        return pd.DataFrame()

    company_year = matched_df.groupby(['ticker', 'year']).agg(agg_dict).reset_index()
    company_year = company_year.rename(columns={'facility_id': 'num_facilities'})

    return company_year

def process_all_files():
    """Main processing function"""
    print("=" * 60)
    print("EPA GHGRP Data Processor")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load S&P 500
    print("\nLoading S&P 500 company list...")
    result = load_sp500_companies()
    if result is None:
        return
    sp500_df, name_to_ticker = result
    sp500_names = list(name_to_ticker.keys())
    print(f"  Loaded {len(sp500_df)} S&P 500 companies")

    # Find GHGRP files
    print("\nSearching for GHGRP data files...")
    files = find_ghgrp_files()

    if not files:
        print(f"\n  No data files found in {RAW_DIR}")
        print("\n  Please download EPA GHGRP data:")
        print("  1. Go to: https://www.epa.gov/ghgreporting/data-sets")
        print("  2. Download 'Data Summary Spreadsheets' for each year")
        print("  3. Extract to: data/epa_ghgrp/raw/")
        print("  4. Run this script again")
        create_sample_data()
        return

    print(f"  Found {len(files)} data files")

    # Process each file
    all_data = []
    for filepath in files:
        print(f"\nProcessing: {filepath.name}")

        df = read_ghgrp_file(filepath)
        if df is None or len(df) == 0:
            continue

        print(f"    Rows: {len(df):,}, Columns: {len(df.columns)}")

        # Standardize columns
        df = standardize_columns(df)

        # Extract year from filename if not in data
        if 'year' not in df.columns:
            year_match = re.search(r'20\d{2}', filepath.name)
            if year_match:
                df['year'] = int(year_match.group())

        # Match to S&P 500
        df = match_to_sp500(df, name_to_ticker, sp500_names)

        all_data.append(df)

    if not all_data:
        print("\nNo data successfully processed")
        return

    # Combine all years
    print("\n" + "=" * 60)
    print("Combining and aggregating data...")
    combined = pd.concat(all_data, ignore_index=True)
    print(f"  Total records: {len(combined):,}")

    # Save facility-level data (matched only)
    facility_data = combined[combined['ticker'].notna()].copy()
    if len(facility_data) > 0:
        facility_file = OUTPUT_DIR / "ghgrp_facilities_matched.csv"
        facility_data.to_csv(facility_file, index=False)
        print(f"  Saved facility data: {facility_file.name} ({len(facility_data):,} rows)")

    # Aggregate to company-year
    company_year = aggregate_by_company_year(combined)
    if len(company_year) > 0:
        company_file = OUTPUT_DIR / "ghgrp_company_year.csv"
        company_year.to_csv(company_file, index=False)
        print(f"  Saved company-year data: {company_file.name} ({len(company_year):,} rows)")

        # Summary stats
        print("\n" + "=" * 60)
        print("Summary Statistics")
        print("=" * 60)
        print(f"  Unique companies: {company_year['ticker'].nunique()}")
        print(f"  Years covered: {company_year['year'].min():.0f} - {company_year['year'].max():.0f}")
        print(f"  Total emissions (all years): {company_year['total_emissions'].sum():,.0f} metric tons CO2e")

        print("\n  Top 10 emitters (total across all years):")
        top_emitters = company_year.groupby('ticker')['total_emissions'].sum().sort_values(ascending=False).head(10)
        for ticker, emissions in top_emitters.items():
            print(f"    {ticker}: {emissions:,.0f} metric tons CO2e")

    print("\nProcessing complete!")
    return company_year

def create_sample_data():
    """Create sample data structure for testing"""
    print("\nCreating sample data structure...")

    # Create sample file to show expected format
    sample = pd.DataFrame({
        'facility_id': [1001, 1002, 1003],
        'facility_name': ['Sample Plant A', 'Sample Plant B', 'Sample Plant C'],
        'parent_company': ['APPLE INC', 'MICROSOFT CORPORATION', 'AMAZON.COM INC'],
        'state': ['CA', 'WA', 'WA'],
        'city': ['Cupertino', 'Redmond', 'Seattle'],
        'total_reported_direct_emissions': [50000, 120000, 250000],
        'primary_naics_code': [334111, 511210, 454110],
        'reporting_year': [2022, 2022, 2022],
        'latitude': [37.33, 47.67, 47.61],
        'longitude': [-122.03, -122.12, -122.33],
    })

    sample_file = RAW_DIR / "SAMPLE_FORMAT.csv"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    sample.to_csv(sample_file, index=False)
    print(f"  Created sample format file: {sample_file}")
    print("  Your EPA GHGRP files should have similar columns")

def check_dependencies():
    """Check if required packages are installed"""
    try:
        from fuzzywuzzy import fuzz
        return True
    except ImportError:
        print("Installing required package: fuzzywuzzy")
        import subprocess
        subprocess.check_call(['pip', 'install', 'fuzzywuzzy', 'python-Levenshtein'])
        return True

if __name__ == "__main__":
    check_dependencies()
    process_all_files()
