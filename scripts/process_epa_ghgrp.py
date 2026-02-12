"""
EPA GHGRP Data Processor
Processes facility-level emissions and matches to S&P 500 firms

INSTRUCTIONS:
1. Download EPA GHGRP data from: https://www.epa.gov/ghgreporting/data-sets
2. Download "Data Summary Spreadsheets" and "Parent Company Data"
3. Extract to: data/epa_ghgrp/raw/
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
        r',.*$',
    ]

    for suffix in suffixes:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)

    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()

    return name

def load_sp500_companies():
    """Load S&P 500 company list"""
    sp500_file = BASE_DIR / "data" / "sp500_constituents.csv"

    if not sp500_file.exists():
        print("ERROR: S&P 500 file not found.")
        return None, None

    df = pd.read_csv(sp500_file)
    df['clean_name'] = df['Security'].apply(clean_company_name)
    df['ticker'] = df['Symbol']

    name_to_ticker = {}
    for _, row in df.iterrows():
        name_to_ticker[row['clean_name']] = row['ticker']
        name_to_ticker[row['ticker']] = row['ticker']

    return df, name_to_ticker

def load_parent_company_data():
    """Load EPA parent company mapping file"""
    print("\nLoading parent company data...")

    # Look for parent company file
    parent_files = list(RAW_DIR.glob("*[Pp]arent*[Cc]ompany*.xls*"))

    if not parent_files:
        print("  WARNING: No parent company file found")
        return None

    parent_file = parent_files[0]
    print(f"  Reading: {parent_file.name}")

    try:
        if parent_file.suffix.lower() == '.xlsb':
            df = pd.read_excel(parent_file, engine='pyxlsb')
        else:
            df = pd.read_excel(parent_file)

        # Standardize column names
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]

        # Rename to standard names
        renames = {
            'ghgrp_facility_id': 'facility_id',
            'parent_company_name': 'parent_company',
            'parent_co._percent_ownership': 'ownership_pct',
            'reporting_year': 'year',
            'facility_naics_code': 'naics_code',
        }
        for old, new in renames.items():
            if old in df.columns:
                df = df.rename(columns={old: new})

        print(f"  Loaded {len(df):,} parent company records")
        print(f"  Years: {df['year'].min():.0f} - {df['year'].max():.0f}")
        print(f"  Unique facilities: {df['facility_id'].nunique():,}")

        return df

    except Exception as e:
        print(f"  Error: {e}")
        return None

def load_emissions_data():
    """Load all yearly emissions files"""
    print("\nLoading emissions data...")

    # Find GHGRP yearly files
    emissions_files = []
    for pattern in ['ghgp_data_20*.xlsx', 'ghgp_data_20*.xls']:
        emissions_files.extend(RAW_DIR.glob(f'**/{pattern}'))

    # Sort by year
    emissions_files = sorted(emissions_files, key=lambda x: x.name)

    if not emissions_files:
        print("  No emissions files found")
        return None

    print(f"  Found {len(emissions_files)} emissions files")

    all_emissions = []

    for filepath in emissions_files:
        # Extract year from filename
        year_match = re.search(r'20\d{2}', filepath.name)
        if not year_match:
            continue

        year = int(year_match.group())
        print(f"  Reading {year}...", end=" ")

        try:
            # These files have 3 header rows
            df = pd.read_excel(filepath, header=3)

            # Standardize column names
            df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]

            # Rename key columns
            renames = {
                'facility_id': 'facility_id',
                'facility_name': 'facility_name',
                'total_reported_direct_emissions': 'total_emissions',
                'primary_naics_code': 'naics_code',
                'state': 'state',
                'latitude': 'latitude',
                'longitude': 'longitude',
            }
            for old, new in renames.items():
                if old in df.columns:
                    df = df.rename(columns={old: new})

            df['year'] = year

            # Keep relevant columns
            keep_cols = ['facility_id', 'facility_name', 'total_emissions', 'naics_code',
                        'state', 'latitude', 'longitude', 'year']
            keep_cols = [c for c in keep_cols if c in df.columns]
            df = df[keep_cols]

            print(f"{len(df):,} facilities")
            all_emissions.append(df)

        except Exception as e:
            print(f"Error: {e}")

    if all_emissions:
        combined = pd.concat(all_emissions, ignore_index=True)
        print(f"\n  Total emissions records: {len(combined):,}")
        return combined

    return None

def match_to_sp500(df, name_to_ticker, sp500_names):
    """Match parent companies to S&P 500 tickers"""
    print("\nMatching companies to S&P 500...")

    if 'parent_company' not in df.columns:
        print("  ERROR: No parent_company column")
        return df

    # Clean names
    df['clean_parent'] = df['parent_company'].apply(clean_company_name)

    # Direct matching
    df['ticker'] = df['clean_parent'].map(name_to_ticker)

    direct_matches = df['ticker'].notna().sum()
    print(f"  Direct matches: {direct_matches:,}")

    # Fuzzy matching for unmatched
    unmatched = df[df['ticker'].isna()]['clean_parent'].unique()
    print(f"  Attempting fuzzy match for {len(unmatched):,} unique companies...")

    fuzzy_matches = {}
    match_count = 0
    for name in unmatched:
        if not name or len(name) < 3:
            continue

        match = process.extractOne(name, sp500_names, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 85:  # 85% similarity threshold
            fuzzy_matches[name] = name_to_ticker.get(match[0])
            match_count += 1

    print(f"  Fuzzy matches found: {match_count}")

    # Apply fuzzy matches
    df['ticker'] = df.apply(
        lambda row: row['ticker'] if pd.notna(row['ticker'])
                    else fuzzy_matches.get(row['clean_parent']),
        axis=1
    )

    total_matched = df['ticker'].notna().sum()
    print(f"  Total matched: {total_matched:,} ({total_matched/len(df)*100:.1f}%)")

    return df

def process_all():
    """Main processing function"""
    print("=" * 60)
    print("EPA GHGRP Data Processor")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load S&P 500
    print("\nLoading S&P 500 company list...")
    sp500_df, name_to_ticker = load_sp500_companies()
    if sp500_df is None:
        return
    sp500_names = list(name_to_ticker.keys())
    print(f"  Loaded {len(sp500_df)} companies")

    # Load parent company data
    parent_df = load_parent_company_data()
    if parent_df is None:
        print("\nCannot proceed without parent company data")
        return

    # Load emissions data
    emissions_df = load_emissions_data()
    if emissions_df is None:
        print("\nCannot proceed without emissions data")
        return

    # Merge emissions with parent company info
    print("\nMerging emissions with parent company data...")
    merged = emissions_df.merge(
        parent_df[['facility_id', 'year', 'parent_company', 'ownership_pct']],
        on=['facility_id', 'year'],
        how='left'
    )
    print(f"  Merged records: {len(merged):,}")
    print(f"  Records with parent company: {merged['parent_company'].notna().sum():,}")

    # Match to S&P 500
    merged = match_to_sp500(merged, name_to_ticker, sp500_names)

    # Save facility-level data (S&P 500 matched only)
    matched_facilities = merged[merged['ticker'].notna()].copy()
    if len(matched_facilities) > 0:
        facility_file = OUTPUT_DIR / "ghgrp_facilities_sp500.csv"
        matched_facilities.to_csv(facility_file, index=False)
        print(f"\nSaved: {facility_file.name} ({len(matched_facilities):,} rows)")

    # Aggregate to company-year level
    print("\nAggregating to company-year level...")
    company_year = matched_facilities.groupby(['ticker', 'year']).agg({
        'total_emissions': 'sum',
        'facility_id': 'nunique',
        'state': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,
    }).reset_index()
    company_year = company_year.rename(columns={
        'facility_id': 'num_facilities',
        'state': 'primary_state'
    })

    if len(company_year) > 0:
        company_file = OUTPUT_DIR / "ghgrp_company_year_sp500.csv"
        company_year.to_csv(company_file, index=False)
        print(f"Saved: {company_file.name} ({len(company_year):,} rows)")

        # Summary
        print("\n" + "=" * 60)
        print("Summary Statistics")
        print("=" * 60)
        print(f"  S&P 500 companies matched: {company_year['ticker'].nunique()}")
        print(f"  Years covered: {company_year['year'].min():.0f} - {company_year['year'].max():.0f}")
        print(f"  Total company-year observations: {len(company_year):,}")

        print("\n  Emissions by year (S&P 500 firms, million metric tons CO2e):")
        yearly = company_year.groupby('year')['total_emissions'].sum() / 1e6
        for year, emissions in yearly.items():
            print(f"    {year:.0f}: {emissions:.1f}")

        print("\n  Top 10 emitters (avg annual, million metric tons):")
        top = company_year.groupby('ticker')['total_emissions'].mean().sort_values(ascending=False).head(10) / 1e6
        for ticker, emissions in top.items():
            print(f"    {ticker}: {emissions:.2f}")

    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)

    return company_year

if __name__ == "__main__":
    process_all()
