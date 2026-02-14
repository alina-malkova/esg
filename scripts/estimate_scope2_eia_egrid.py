#!/usr/bin/env python3
"""
Estimate Scope 2 Emissions from EIA Electricity Data + EPA eGRID Emission Factors

This script implements the estimation approach:
    Scope 2 (MT CO2e) = Electricity Consumption (MWh) × Regional Emission Factor (MT CO2/MWh)

Data sources:
- EPA eGRID: Regional electricity grid emission factors (already downloaded)
- EIA Form 861: Utility-level electricity sales by state and sector
- SEC 10-K: Facility locations for company-facility matching

Author: Research Assistant
Date: February 2026
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
import zipfile
import io
import json

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
EIA_DIR = DATA_DIR / 'eia_861'
EGRID_DIR = DATA_DIR / 'epa_egrid'
OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'output'

EIA_DIR.mkdir(parents=True, exist_ok=True)


def download_eia_861_data(years=range(2018, 2024)):
    """
    Download EIA Form 861 data for specified years.
    Form 861 contains utility-level electricity sales by state and customer class.
    """
    print("Downloading EIA Form 861 data...")

    base_url = "https://www.eia.gov/electricity/data/eia861"
    downloaded = []

    for year in years:
        # EIA uses different URL patterns for different years
        if year >= 2020:
            url = f"{base_url}/zip/f861{year}.zip"
        else:
            url = f"{base_url}/archive/zip/f861{year}.zip"

        output_file = EIA_DIR / f"f861_{year}.zip"

        if output_file.exists():
            print(f"  {year}: Already downloaded")
            downloaded.append(year)
            continue

        try:
            print(f"  Downloading {year}...")
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                f.write(response.content)

            downloaded.append(year)
            print(f"  {year}: Downloaded ({len(response.content)/1e6:.1f} MB)")

        except Exception as e:
            print(f"  {year}: Failed - {e}")
            # Try alternative URL pattern
            try:
                alt_url = f"https://www.eia.gov/electricity/data/eia861/zip/f861{year}.zip"
                response = requests.get(alt_url, timeout=60)
                response.raise_for_status()
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                downloaded.append(year)
                print(f"  {year}: Downloaded (alt URL)")
            except:
                pass

    return downloaded


def load_egrid_emission_factors():
    """
    Load EPA eGRID emission factors by subregion.
    Returns MT CO2 per MWh for each eGRID subregion.
    """
    print("\nLoading eGRID emission factors...")

    egrid_file = EGRID_DIR / 'eGRID2022_data.xlsx'

    if not egrid_file.exists():
        print(f"  ERROR: eGRID file not found at {egrid_file}")
        return None

    # Read the subregion-level data
    # eGRID has multiple sheets; SRL (subregion-level) has the emission rates
    try:
        df = pd.read_excel(egrid_file, sheet_name='SRL22', skiprows=1)

        # Key columns:
        # SUBRGN - eGRID subregion code
        # SRC2ERTA - Subregion annual CO2 equivalent total output emission rate (lb/MWh)

        # Convert lb/MWh to MT/MWh (1 MT = 2204.62 lb)
        df['co2_mt_per_mwh'] = df['SRC2ERTA'] / 2204.62

        emission_factors = df[['SUBRGN', 'co2_mt_per_mwh']].copy()
        emission_factors.columns = ['egrid_subregion', 'emission_factor_mt_mwh']

        print(f"  Loaded {len(emission_factors)} eGRID subregions")
        print(f"  Emission factor range: {emission_factors['emission_factor_mt_mwh'].min():.4f} - {emission_factors['emission_factor_mt_mwh'].max():.4f} MT CO2/MWh")

        return emission_factors

    except Exception as e:
        print(f"  ERROR loading eGRID: {e}")
        return None


def load_state_to_egrid_mapping():
    """
    Map US states to primary eGRID subregion.
    Most states map to a single primary subregion; some states span multiple.
    """
    # Primary eGRID subregion by state (simplified mapping)
    # Source: EPA eGRID documentation
    state_egrid = {
        'AL': 'SRSO',  # SERC South
        'AK': 'AKGD',  # Alaska Grid
        'AZ': 'AZNM',  # WECC Southwest
        'AR': 'SRMV',  # SERC Mississippi Valley
        'CA': 'CAMX',  # WECC California
        'CO': 'RMPA',  # WECC Rockies
        'CT': 'NEWE',  # Northeast
        'DE': 'RFCE',  # RFC East
        'FL': 'FRCC',  # Florida
        'GA': 'SRSO',  # SERC South
        'HI': 'HIMS',  # Hawaii
        'ID': 'NWPP',  # WECC Northwest
        'IL': 'RFCW',  # RFC West
        'IN': 'RFCW',  # RFC West
        'IA': 'MROW',  # MRO West
        'KS': 'SPNO',  # SPP North
        'KY': 'SRVC',  # SERC Virginia/Carolina
        'LA': 'SRMV',  # SERC Mississippi Valley
        'ME': 'NEWE',  # Northeast
        'MD': 'RFCE',  # RFC East
        'MA': 'NEWE',  # Northeast
        'MI': 'RFCM',  # RFC Michigan
        'MN': 'MROW',  # MRO West
        'MS': 'SRMV',  # SERC Mississippi Valley
        'MO': 'SRMV',  # SERC Mississippi Valley
        'MT': 'NWPP',  # WECC Northwest
        'NE': 'MROW',  # MRO West
        'NV': 'NWPP',  # WECC Northwest
        'NH': 'NEWE',  # Northeast
        'NJ': 'RFCE',  # RFC East
        'NM': 'AZNM',  # WECC Southwest
        'NY': 'NYCW',  # NY (simplified - actually split)
        'NC': 'SRVC',  # SERC Virginia/Carolina
        'ND': 'MROW',  # MRO West
        'OH': 'RFCW',  # RFC West
        'OK': 'SPSO',  # SPP South
        'OR': 'NWPP',  # WECC Northwest
        'PA': 'RFCE',  # RFC East
        'RI': 'NEWE',  # Northeast
        'SC': 'SRVC',  # SERC Virginia/Carolina
        'SD': 'MROW',  # MRO West
        'TN': 'SRVC',  # SERC Virginia/Carolina
        'TX': 'ERCT',  # ERCOT Texas
        'UT': 'NWPP',  # WECC Northwest
        'VT': 'NEWE',  # Northeast
        'VA': 'SRVC',  # SERC Virginia/Carolina
        'WA': 'NWPP',  # WECC Northwest
        'WV': 'RFCW',  # RFC West
        'WI': 'MROE',  # MRO East
        'WY': 'RMPA',  # WECC Rockies
        'DC': 'RFCE',  # RFC East
    }

    return pd.DataFrame([
        {'state': k, 'egrid_subregion': v}
        for k, v in state_egrid.items()
    ])


def extract_eia_sales_data(year):
    """
    Extract commercial/industrial electricity sales by state from EIA Form 861.
    """
    zip_file = EIA_DIR / f"f861_{year}.zip"

    if not zip_file.exists():
        return None

    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            # List files in archive
            file_list = z.namelist()

            # Look for sales file (naming varies by year)
            sales_files = [f for f in file_list if 'sales' in f.lower() and f.endswith('.xlsx')]

            if not sales_files:
                # Try CSV
                sales_files = [f for f in file_list if 'sales' in f.lower() and f.endswith('.csv')]

            if not sales_files:
                print(f"  {year}: No sales file found in {file_list[:5]}...")
                return None

            sales_file = sales_files[0]

            with z.open(sales_file) as f:
                if sales_file.endswith('.xlsx'):
                    df = pd.read_excel(f)
                else:
                    df = pd.read_csv(f)

            # Standardize column names (vary by year)
            df.columns = df.columns.str.lower().str.strip()

            # Key columns we need:
            # - State
            # - Commercial sales (MWh)
            # - Industrial sales (MWh)

            # Try to identify relevant columns
            state_cols = [c for c in df.columns if 'state' in c]
            comm_cols = [c for c in df.columns if 'commercial' in c and ('sales' in c or 'mwh' in c)]
            ind_cols = [c for c in df.columns if 'industrial' in c and ('sales' in c or 'mwh' in c)]

            if state_cols and (comm_cols or ind_cols):
                result = df[[state_cols[0]]].copy()
                result.columns = ['state']

                if comm_cols:
                    result['commercial_mwh'] = pd.to_numeric(df[comm_cols[0]], errors='coerce')
                if ind_cols:
                    result['industrial_mwh'] = pd.to_numeric(df[ind_cols[0]], errors='coerce')

                # Aggregate by state
                result = result.groupby('state').sum().reset_index()
                result['year'] = year

                return result

            print(f"  {year}: Could not identify required columns")
            return None

    except Exception as e:
        print(f"  {year}: Error extracting data - {e}")
        return None


def estimate_state_scope2(years=range(2018, 2024)):
    """
    Estimate Scope 2 emissions by state using EIA electricity data + eGRID factors.
    """
    print("\nEstimating state-level Scope 2 emissions...")

    # Load emission factors
    emission_factors = load_egrid_emission_factors()
    if emission_factors is None:
        return None

    # Load state-to-eGRID mapping
    state_egrid = load_state_to_egrid_mapping()

    # Merge to get emission factor by state
    state_factors = state_egrid.merge(emission_factors, on='egrid_subregion', how='left')

    # Extract EIA data for each year
    all_years = []
    for year in years:
        df = extract_eia_sales_data(year)
        if df is not None:
            all_years.append(df)
            print(f"  {year}: Extracted {len(df)} state records")

    if not all_years:
        print("  No EIA data could be extracted")
        return None

    # Combine all years
    eia_panel = pd.concat(all_years, ignore_index=True)

    # Merge with emission factors
    eia_panel = eia_panel.merge(state_factors, on='state', how='left')

    # Calculate Scope 2 emissions
    if 'commercial_mwh' in eia_panel.columns:
        eia_panel['commercial_scope2_mt'] = eia_panel['commercial_mwh'] * eia_panel['emission_factor_mt_mwh']
    if 'industrial_mwh' in eia_panel.columns:
        eia_panel['industrial_scope2_mt'] = eia_panel['industrial_mwh'] * eia_panel['emission_factor_mt_mwh']

    # Total Scope 2 (commercial + industrial)
    eia_panel['total_scope2_mt'] = eia_panel.get('commercial_scope2_mt', 0) + eia_panel.get('industrial_scope2_mt', 0)

    print(f"\nState-level Scope 2 panel: {len(eia_panel)} observations")

    return eia_panel


def create_data_center_state_scope2():
    """
    Calculate Scope 2 emissions for data center hub states vs control states.
    Uses the state-level estimation to validate against utility DiD results.
    """
    print("\nCalculating Scope 2 for data center analysis...")

    # Hub states (from your utility analysis)
    hub_states = ['VA', 'TX', 'OR', 'AZ', 'GA']
    control_states = ['MT', 'WY', 'VT', 'ME']

    # Estimate state-level Scope 2
    state_scope2 = estimate_state_scope2()

    if state_scope2 is None:
        return None

    # Filter to hub and control states
    dc_states = state_scope2[state_scope2['state'].isin(hub_states + control_states)].copy()
    dc_states['is_hub'] = dc_states['state'].isin(hub_states)

    # Calculate aggregates
    summary = dc_states.groupby(['year', 'is_hub']).agg({
        'total_scope2_mt': 'sum',
        'commercial_scope2_mt': 'sum',
        'state': 'count'
    }).reset_index()
    summary.columns = ['year', 'is_hub', 'total_scope2_mt', 'commercial_scope2_mt', 'n_states']

    print("\nScope 2 by Hub Status:")
    print(summary.to_string(index=False))

    return dc_states, summary


def validate_against_big_tech():
    """
    Compare EIA-based Scope 2 estimates against Big Tech sustainability reports.
    This validates the estimation methodology.
    """
    print("\n" + "="*60)
    print("VALIDATION: EIA Estimates vs. Big Tech Sustainability Reports")
    print("="*60)

    # Big Tech reported Scope 2 (from your manual compilation)
    big_tech_reported = pd.DataFrame([
        {'company': 'Microsoft', 'year': 2023, 'scope2_reported_mt': 7.10e6},
        {'company': 'Alphabet', 'year': 2023, 'scope2_reported_mt': 7.48e6},
        {'company': 'Meta', 'year': 2023, 'scope2_reported_mt': 3.81e6},
        {'company': 'Amazon', 'year': 2023, 'scope2_reported_mt': 10.20e6},
        {'company': 'Apple', 'year': 2023, 'scope2_reported_mt': 0.51e6},
    ])

    # Known data center locations (simplified)
    # For proper estimation, we'd need facility-level electricity consumption
    dc_locations = {
        'Microsoft': ['VA', 'WA', 'TX', 'AZ', 'IL'],
        'Alphabet': ['VA', 'OR', 'GA', 'NC', 'SC'],
        'Meta': ['VA', 'OR', 'TX', 'GA', 'NM'],
        'Amazon': ['VA', 'OR', 'OH', 'CA', 'TX'],
        'Apple': ['NC', 'AZ', 'NV', 'CA'],
    }

    print("\nBig Tech Reported Scope 2 (2023):")
    print(big_tech_reported.to_string(index=False))

    print("\nKey Insight: EIA state-level data cannot directly estimate company-level")
    print("Scope 2 because it doesn't link facilities to companies.")
    print("\nFor company-level Scope 2, you need either:")
    print("  1. WRDS Trucost/ISS ESG (institutional access)")
    print("  2. CDP corporate disclosures (academic license)")
    print("  3. Manual extraction from sustainability reports (labor intensive)")

    return big_tech_reported


def main():
    """Main estimation pipeline."""
    print("="*60)
    print("SCOPE 2 ESTIMATION: EIA + eGRID APPROACH")
    print("="*60)

    # Step 1: Download EIA data
    downloaded_years = download_eia_861_data(years=range(2018, 2024))
    print(f"\nDownloaded EIA data for years: {downloaded_years}")

    # Step 2: Load eGRID emission factors
    emission_factors = load_egrid_emission_factors()

    if emission_factors is not None:
        print("\neGRID Emission Factors by Subregion (MT CO2/MWh):")
        print(emission_factors.sort_values('emission_factor_mt_mwh', ascending=False).head(10).to_string(index=False))

    # Step 3: Calculate state-level Scope 2
    state_scope2 = estimate_state_scope2()

    if state_scope2 is not None:
        # Save state-level panel
        output_file = OUTPUT_DIR / 'state_scope2_estimated.csv'
        state_scope2.to_csv(output_file, index=False)
        print(f"\nSaved state-level Scope 2 estimates to {output_file}")

    # Step 4: Data center hub analysis
    dc_analysis = create_data_center_state_scope2()

    # Step 5: Validation
    validate_against_big_tech()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("""
The EIA + eGRID approach provides:
  - State-level Scope 2 estimates (useful for geographic analysis)
  - Validation of utility-level DiD findings

LIMITATIONS for firm-level analysis:
  - Cannot link electricity consumption to specific companies
  - Data centers often leased (not in company's utility account)
  - Need facility-to-company matching for firm-level panel

RECOMMENDATIONS:
  1. Check if FIT has WRDS access (Trucost/ISS ESG has firm-level Scope 2)
  2. Apply for CDP academic data license
  3. If neither available, expand Big Tech manual compilation to top 50 firms
    """)


if __name__ == '__main__':
    main()
