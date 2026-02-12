"""
Process CDP Scope 2 Emissions Data
==================================

CDP data provides Scope 2 (purchased electricity) emissions which captures
data center energy use that GHGRP (Scope 1 only) misses.

Available data: 2010-2013 (pre-ChatGPT)
Needed: 2018-2023 for full diff-in-diff analysis

This script:
1. Processes existing CDP data (2010-2013)
2. Matches to S&P 500 companies
3. Creates combined Scope 1 + Scope 2 emissions panel
4. Identifies gaps for future data collection
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

DATA_DIR = Path(__file__).parent.parent / "data"
CDP_DIR = DATA_DIR / "cdp"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis" / "output"

def clean_ticker(ticker):
    """Clean ticker symbol for matching."""
    if pd.isna(ticker):
        return None
    ticker = str(ticker).upper().strip()
    # Remove exchange suffix (e.g., "AAPL US" -> "AAPL")
    ticker = ticker.split()[0] if ' ' in ticker else ticker
    return ticker

def load_cdp_carbon_action():
    """Load 2010-2013 carbon action emissions data."""
    df = pd.read_csv(CDP_DIR / "2010_2013_carbon_action_emissions.csv")

    # Clean and standardize
    df['ticker'] = df['ticker_symbol'].apply(clean_ticker)
    df['year'] = df['accounting_year']

    # Combine reported and estimated values (prefer reported)
    df['scope_1'] = df['reported_scope_1_metric_tonnes_co2e'].fillna(
        df['estimated_scope_1_metric_tonnes_co2e']
    )
    df['scope_2'] = df['reported_scope_2_metric_tonnes_co2e'].fillna(
        df['estimated_scope_2_metric_tonnes_co2e']
    )

    # Convert to numeric
    df['scope_1'] = pd.to_numeric(df['scope_1'], errors='coerce')
    df['scope_2'] = pd.to_numeric(df['scope_2'], errors='coerce')

    return df[['company_name', 'ticker', 'country', 'year', 'industry_activity_group',
               'scope_1', 'scope_2']].copy()

def load_cdp_global500():
    """Load Global 500 emissions data for 2011-2013."""
    dfs = []
    for year in [2011, 2012, 2013]:
        file_path = CDP_DIR / f"{year}_global500_emissions.csv"
        if file_path.exists():
            df = pd.read_csv(file_path)
            df['year'] = year
            df['ticker'] = df['ticker_symbol'].apply(clean_ticker)
            df['scope_1'] = pd.to_numeric(df['scope_1_metric_tonnes_co2e'], errors='coerce')
            df['scope_2'] = pd.to_numeric(df['scope_2_metric_tonnes_co2e'], errors='coerce')
            dfs.append(df[['company_name', 'ticker', 'country', 'year', 'scope_1', 'scope_2']])

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def match_to_sp500(cdp_df, sp500_df):
    """Match CDP companies to S&P 500 tickers."""
    # Direct ticker match
    matched = cdp_df.merge(
        sp500_df[['Symbol', 'Security', 'GICS Sector']],
        left_on='ticker', right_on='Symbol', how='inner'
    )
    return matched

def main():
    print("=" * 70)
    print("PROCESSING CDP SCOPE 2 EMISSIONS DATA")
    print("=" * 70)

    # Load S&P 500 list
    sp500 = pd.read_csv(DATA_DIR / "sp500_constituents.csv")
    print(f"\nS&P 500 companies: {len(sp500)}")

    # Load CDP data sources
    print("\n1. Loading CDP data sources...")

    # Carbon action data (2010-2013)
    carbon_action = load_cdp_carbon_action()
    print(f"   Carbon Action 2010-2013: {len(carbon_action)} records, {carbon_action['company_name'].nunique()} companies")

    # Global 500 data
    global500 = load_cdp_global500()
    print(f"   Global 500 2011-2013: {len(global500)} records")

    # Combine all CDP data
    cdp_all = pd.concat([carbon_action, global500], ignore_index=True)
    cdp_all = cdp_all.drop_duplicates(subset=['ticker', 'year'], keep='first')
    print(f"\n   Combined CDP data: {len(cdp_all)} company-year observations")

    # Match to S&P 500
    print("\n2. Matching to S&P 500...")
    cdp_sp500 = match_to_sp500(cdp_all, sp500)
    print(f"   Matched to S&P 500: {len(cdp_sp500)} observations")
    print(f"   Unique S&P 500 firms: {cdp_sp500['Symbol'].nunique()}")

    # Summary statistics
    print("\n" + "=" * 70)
    print("CDP SCOPE 2 SUMMARY (S&P 500 Matches)")
    print("=" * 70)

    # Coverage by year
    print("\n--- Coverage by Year ---")
    year_summary = cdp_sp500.groupby('year').agg({
        'Symbol': 'nunique',
        'scope_1': lambda x: x.notna().sum(),
        'scope_2': lambda x: x.notna().sum()
    })
    year_summary.columns = ['N Firms', 'Scope 1 Available', 'Scope 2 Available']
    print(year_summary.to_string())

    # Scope 1 vs Scope 2 comparison
    print("\n--- Scope 1 vs Scope 2 Comparison ---")
    valid_both = cdp_sp500[cdp_sp500['scope_1'].notna() & cdp_sp500['scope_2'].notna()]
    if len(valid_both) > 0:
        print(f"   Firms with both scopes: {len(valid_both)}")
        print(f"   Mean Scope 1: {valid_both['scope_1'].mean()/1e6:.2f} M tonnes CO2e")
        print(f"   Mean Scope 2: {valid_both['scope_2'].mean()/1e6:.2f} M tonnes CO2e")
        print(f"   Scope 2 / Scope 1 ratio: {valid_both['scope_2'].sum() / valid_both['scope_1'].sum():.2f}")

    # By sector
    print("\n--- Scope 2 Intensity by Sector ---")
    sector_summary = cdp_sp500.groupby('GICS Sector').agg({
        'Symbol': 'nunique',
        'scope_2': ['mean', 'sum']
    }).round(0)
    sector_summary.columns = ['N Firms', 'Mean Scope 2', 'Total Scope 2']
    sector_summary = sector_summary.sort_values('Mean Scope 2', ascending=False)
    print(sector_summary.to_string())

    # Load GHGRP data for comparison
    print("\n3. Comparing with GHGRP Scope 1 data...")
    ghgrp = pd.read_csv(DATA_DIR / "epa_ghgrp/processed/ghgrp_company_year_sp500_all_years.csv")
    ghgrp_2011_2013 = ghgrp[ghgrp['year'].isin([2011, 2012, 2013])]

    # Merge CDP and GHGRP
    ghgrp_2011_2013 = ghgrp_2011_2013.rename(columns={'ticker': 'ghgrp_ticker'})
    merged = cdp_sp500.merge(
        ghgrp_2011_2013[['ghgrp_ticker', 'year', 'total_emissions']],
        left_on=['Symbol', 'year'], right_on=['ghgrp_ticker', 'year'],
        how='outer'
    )

    # Compare Scope 1 sources
    both_scope1 = merged[merged['scope_1'].notna() & merged['total_emissions'].notna()]
    if len(both_scope1) > 0:
        print(f"\n   Firms with both CDP and GHGRP Scope 1: {len(both_scope1)}")
        corr = both_scope1['scope_1'].corr(both_scope1['total_emissions'])
        print(f"   Correlation between CDP and GHGRP Scope 1: {corr:.3f}")

    # Save processed CDP data
    print("\n4. Saving processed data...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # CDP S&P 500 emissions
    cdp_output = cdp_sp500[['Symbol', 'Security', 'GICS Sector', 'year', 'scope_1', 'scope_2']].copy()
    cdp_output.columns = ['ticker', 'company', 'gics_sector', 'year', 'cdp_scope_1', 'cdp_scope_2']
    cdp_output['total_cdp'] = cdp_output['cdp_scope_1'].fillna(0) + cdp_output['cdp_scope_2'].fillna(0)
    cdp_output.to_csv(OUTPUT_DIR / 'cdp_emissions_sp500.csv', index=False)
    print(f"   Saved: cdp_emissions_sp500.csv ({len(cdp_output)} records)")

    # Combined GHGRP + CDP panel (where available)
    combined = ghgrp.copy()
    combined = combined.merge(
        cdp_output[['ticker', 'year', 'cdp_scope_1', 'cdp_scope_2']],
        on=['ticker', 'year'], how='left'
    )
    combined['scope_1_best'] = combined['total_emissions']  # GHGRP is authoritative for Scope 1
    combined['total_with_scope2'] = combined['total_emissions'] + combined['cdp_scope_2'].fillna(0)

    combined.to_csv(OUTPUT_DIR / 'emissions_combined_panel.csv', index=False)
    print(f"   Saved: emissions_combined_panel.csv ({len(combined)} records)")

    # Data gaps report
    print("\n" + "=" * 70)
    print("DATA GAPS FOR DIFF-IN-DIFF ANALYSIS")
    print("=" * 70)
    print("""
AVAILABLE DATA:
- GHGRP Scope 1: 2010-2023 (complete for analysis)
- CDP Scope 1+2: 2010-2013 only

MISSING FOR POST-CHATGPT ANALYSIS:
- CDP Scope 2: 2018-2023 needed
- Key firms needing Scope 2: GOOGL, META, MSFT, AMZN (data centers)

OPTIONS TO OBTAIN SCOPE 2 DATA:
1. CDP Data Portal (requires registration): https://data.cdp.net/
2. Corporate sustainability reports (manual collection)
3. Bloomberg/Refinitiv ESG (subscription required)
4. EPA eGRID + facility electricity use (calculate Scope 2)

WORKAROUND FOR CURRENT ANALYSIS:
- Use GHGRP Scope 1 as proxy (captures direct emissions)
- Note limitation: Tech firm data center emissions not fully captured
- Focus on sectors where Scope 1 dominates (Utilities, Energy, Materials)
""")

    print("\n" + "=" * 70)
    print("PROCESSING COMPLETE")
    print("=" * 70)

    return cdp_output, combined

if __name__ == "__main__":
    cdp_data, combined = main()
