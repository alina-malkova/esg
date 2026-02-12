"""
Process EPA GHGRP data for all years (2010-2023) and match to S&P 500 companies.

Strategy: Use 2023 parent company data and apply it to all years via stable facility IDs.

Outputs:
- ghgrp_facilities_all_years.csv: All facilities with emissions by year
- ghgrp_facilities_sp500_all_years.csv: S&P 500 matched facilities with emissions by year
- ghgrp_company_year_sp500_all_years.csv: Company-year aggregated emissions for S&P 500
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
GHGRP_DIR = DATA_DIR / "epa_ghgrp"
RAW_DIR = GHGRP_DIR / "raw"
SUMMARY_DIR = RAW_DIR / "2023 Data Summary Spreadsheets"
PROCESSED_DIR = GHGRP_DIR / "processed"

def load_sp500():
    """Load S&P 500 constituents with cleaned company names for matching."""
    df = pd.read_csv(DATA_DIR / "sp500_constituents.csv")
    df['clean_name'] = df['Security'].str.upper().str.strip()
    df['clean_name_short'] = df['clean_name'].str.replace(r'\s+(CORP|CORPORATION|INC|CO|COMPANY|LTD|LLC|PLC|&)\.?$', '', regex=True)
    return df

def load_parent_company_data():
    """Load parent company ownership data (2023 only, applied to all years)."""
    parent_file = RAW_DIR / "EPA Parent Company Data.xlsb"
    df = pd.read_excel(parent_file, engine='pyxlsb')
    df.columns = [c.strip() for c in df.columns]

    # Clean parent company names
    df['clean_parent'] = (df['PARENT COMPANY NAME']
        .str.upper()
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .str.replace(r'\.$', '', regex=True))

    return df

def build_ticker_matcher(sp500_df):
    """Build function to match parent company names to S&P 500 tickers."""
    matches = {}

    # Direct matching from S&P 500 list
    for _, row in sp500_df.iterrows():
        ticker = row['Symbol']
        name = row['clean_name']
        name_short = row['clean_name_short']
        security = row['Security'].upper()

        patterns = [name, name_short, security, name.replace(' ', ''), name_short.replace(' ', '')]
        for pattern in patterns:
            if pattern and len(pattern) > 2:
                matches[pattern] = ticker

    # Extensive manual matches for major companies
    manual_matches = {
        '3M': 'MMM', '3M CO': 'MMM', '3M COMPANY': 'MMM',
        'ABBOTT LABORATORIES': 'ABT', 'ABBOTT': 'ABT',
        'ABBVIE': 'ABBV', 'ABBVIE INC': 'ABBV',
        'ALPHABET': 'GOOGL', 'ALPHABET INC': 'GOOGL', 'GOOGLE': 'GOOGL',
        'AMAZON': 'AMZN', 'AMAZON.COM': 'AMZN', 'AMAZON COM': 'AMZN',
        'APPLE': 'AAPL', 'APPLE INC': 'AAPL',
        'ARCHER DANIELS MIDLAND': 'ADM', 'ADM': 'ADM',
        'AT&T': 'T', 'ATT': 'T',
        'BANK OF AMERICA': 'BAC',
        'BERKSHIRE HATHAWAY': 'BRK.B', 'BERKSHIRE HATHAWAY INC': 'BRK.B',
        'BOEING': 'BA', 'BOEING CO': 'BA',
        'BRISTOL MYERS SQUIBB': 'BMY', 'BRISTOL-MYERS SQUIBB': 'BMY',
        'CATERPILLAR': 'CAT', 'CATERPILLAR INC': 'CAT',
        'CENTERPOINT ENERGY': 'CNP', 'CENTERPOINT ENERGY INC': 'CNP',
        'CHEVRON': 'CVX', 'CHEVRON CORP': 'CVX', 'CHEVRON CORPORATION': 'CVX',
        'COCA-COLA': 'KO', 'COCA COLA': 'KO',
        'COMCAST': 'CMCSA', 'COMCAST CORP': 'CMCSA',
        'CONOCOPHILLIPS': 'COP', 'CONOCO PHILLIPS': 'COP',
        'CONSOLIDATED EDISON': 'ED', 'CON EDISON': 'ED',
        'DELTA AIR LINES': 'DAL', 'DELTA': 'DAL',
        'DEVON ENERGY': 'DVN',
        'DOMINION ENERGY': 'D', 'DOMINION': 'D',
        'DOW': 'DOW', 'DOW INC': 'DOW', 'DOW CHEMICAL': 'DOW',
        'DTE ENERGY': 'DTE',
        'DUKE ENERGY': 'DUK', 'DUKE ENERGY CORP': 'DUK',
        'DUPONT': 'DD', 'DU PONT': 'DD',
        'EASTMAN CHEMICAL': 'EMN',
        'ENTERGY': 'ETR', 'ENTERGY CORP': 'ETR',
        'EOG RESOURCES': 'EOG',
        'EXXON': 'XOM', 'EXXON MOBIL': 'XOM', 'EXXONMOBIL': 'XOM',
        'FIRSTENERGY': 'FE', 'FIRST ENERGY': 'FE',
        'FORD': 'F', 'FORD MOTOR': 'F',
        'FREEPORT-MCMORAN': 'FCX', 'FREEPORT MCMORAN': 'FCX',
        'GENERAL ELECTRIC': 'GE',
        'GENERAL MILLS': 'GIS',
        'GENERAL MOTORS': 'GM',
        'GOLDMAN SACHS': 'GS',
        'HALLIBURTON': 'HAL',
        'HCA HEALTHCARE': 'HCA', 'HCA': 'HCA',
        'HONEYWELL': 'HON',
        'INTEL': 'INTC', 'INTEL CORP': 'INTC',
        'INTERNATIONAL PAPER': 'IP',
        'JOHNSON & JOHNSON': 'JNJ', 'J&J': 'JNJ',
        'JPMORGAN': 'JPM', 'JP MORGAN': 'JPM', 'JPMORGAN CHASE': 'JPM',
        'KIMBERLY-CLARK': 'KMB', 'KIMBERLY CLARK': 'KMB',
        'KINDER MORGAN': 'KMI',
        'LINDE': 'LIN', 'LINDE PLC': 'LIN',
        'LOCKHEED MARTIN': 'LMT',
        'MARATHON PETROLEUM': 'MPC',
        'MERCK': 'MRK', 'MERCK & CO': 'MRK',
        'META': 'META', 'META PLATFORMS': 'META', 'FACEBOOK': 'META',
        'MICRON': 'MU', 'MICRON TECHNOLOGY': 'MU',
        'MICROSOFT': 'MSFT',
        'NEXTERA ENERGY': 'NEE', 'NEXTERA': 'NEE',
        'NEWMONT': 'NEM', 'NEWMONT MINING': 'NEM',
        'NORTHROP GRUMMAN': 'NOC',
        'NUCOR': 'NUE',
        'NVIDIA': 'NVDA',
        'OCCIDENTAL PETROLEUM': 'OXY', 'OCCIDENTAL': 'OXY',
        'ONEOK': 'OKE',
        'PACCAR': 'PCAR',
        'PACIFIC GAS & ELECTRIC': 'PCG', 'PG&E': 'PCG', 'PGE': 'PCG',
        'PEPSICO': 'PEP', 'PEPSI': 'PEP',
        'PFIZER': 'PFE',
        'PHILLIPS 66': 'PSX',
        'PROCTER & GAMBLE': 'PG', 'P&G': 'PG',
        'QUALCOMM': 'QCOM',
        'RAYTHEON': 'RTX',
        'REPUBLIC SERVICES': 'RSG',
        'TESLA': 'TSLA', 'TESLA INC': 'TSLA',
        'TEXAS INSTRUMENTS': 'TXN',
        'THERMO FISHER': 'TMO', 'THERMO FISHER SCIENTIFIC': 'TMO',
        'TYSON FOODS': 'TSN', 'TYSON': 'TSN',
        'UNION PACIFIC': 'UNP',
        'UNITED PARCEL SERVICE': 'UPS', 'UPS': 'UPS',
        'VALERO ENERGY': 'VLO', 'VALERO': 'VLO',
        'VERIZON': 'VZ',
        'WALMART': 'WMT', 'WAL-MART': 'WMT',
        'WASTE MANAGEMENT': 'WM',
        'WEC ENERGY': 'WEC', 'WEC ENERGY GROUP': 'WEC',
        'XCEL ENERGY': 'XEL',
        'ALLIANT ENERGY': 'LNT',
        'AMEREN': 'AEE', 'AMEREN CORP': 'AEE',
        'AMERICAN ELECTRIC POWER': 'AEP', 'AEP': 'AEP',
        'AES': 'AES', 'AES CORP': 'AES',
        'CF INDUSTRIES': 'CF',
        'CMS ENERGY': 'CMS',
        'CONSTELLATION ENERGY': 'CEG',
        'EVERGY': 'EVRG',
        'LILLY': 'LLY', 'ELI LILLY': 'LLY',
        'MARTIN MARIETTA': 'MLM',
        'NRG ENERGY': 'NRG', 'NRG': 'NRG',
        'NISOURCE': 'NI',
        'PINNACLE WEST': 'PNW', 'PINNACLE WEST CAPITAL': 'PNW',
        'PPL': 'PPL', 'PPL CORP': 'PPL',
        'STEEL DYNAMICS': 'STLD',
        'TARGA RESOURCES': 'TRGP',
        'VISTRA': 'VST', 'VISTRA CORP': 'VST',
        'AMGEN': 'AMGN',
        'APA': 'APA', 'APA CORP': 'APA', 'APACHE': 'APA',
        'ATMOS ENERGY': 'ATO',
        'BROADCOM': 'AVGO',
        'BAXTER': 'BAX', 'BAXTER INTERNATIONAL': 'BAX',
        'BROWN-FORMAN': 'BF.B', 'BROWN FORMAN': 'BF.B',
        'BIOGEN': 'BIIB',
        'BLACKROCK': 'BLK',
        'CONAGRA': 'CAG', 'CONAGRA BRANDS': 'CAG',
        'CORTEVA': 'CTVA',
        'CAESARS': 'CZR', 'CAESARS ENTERTAINMENT': 'CZR',
        'DEERE': 'DE', 'JOHN DEERE': 'DE',
        'ESSEX PROPERTY': 'ESS',
        'CORNING': 'GLW',
        'HORMEL': 'HRL', 'HORMEL FOODS': 'HRL',
        'HOWMET': 'HWM', 'HOWMET AEROSPACE': 'HWM',
        'IFF': 'IFF', 'INTERNATIONAL FLAVORS': 'IFF',
        'ILLINOIS TOOL WORKS': 'ITW', 'ITW': 'ITW',
        'LOEWS': 'L',
        'LAMB WESTON': 'LW',
        'MARRIOTT': 'MAR',
        'MICROCHIP': 'MCHP', 'MICROCHIP TECHNOLOGY': 'MCHP',
        'MOHAWK': 'MHK', 'MOHAWK INDUSTRIES': 'MHK',
        'ALTRIA': 'MO',
        'NXP': 'NXPI', 'NXP SEMICONDUCTORS': 'NXPI',
        'ON SEMICONDUCTOR': 'ON', 'ONSEMI': 'ON',
        'PUBLIC SERVICE ENTERPRISE': 'PEG', 'PSEG': 'PEG',
        'PPG': 'PPG', 'PPG INDUSTRIES': 'PPG',
        'SKYWORKS': 'SWKS', 'SKYWORKS SOLUTIONS': 'SWKS',
        'MOLSON COORS': 'TAP',
        'TEXTRON': 'TXT',
        'VIATRIS': 'VTRS',
        'WEYERHAEUSER': 'WY',
        'HUNTINGTON INGALLS': 'HII',
        'GE VERNOVA': 'GEV',
        'SOUTHERN': 'SO', 'SOUTHERN COMPANY': 'SO', 'SOUTHERN CO': 'SO',
        'ACUITY BRANDS': 'AYI',
        'ANALOG DEVICES': 'ADI',
    }
    matches.update(manual_matches)

    def find_match(parent_name):
        if pd.isna(parent_name):
            return None
        name = str(parent_name).upper().strip()

        # Direct match
        if name in matches:
            return matches[name]

        # Remove common suffixes and try again
        cleaned = re.sub(r'\s+(CORP|CORPORATION|INC|CO|COMPANY|LTD|LLC|PLC|LP|&|HOLDING|HOLDINGS|GROUP|ENTERPRISES?)\.?$', '', name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if cleaned in matches:
            return matches[cleaned]

        # Try partial matching for key words
        for key, ticker in matches.items():
            if len(key) > 5 and key in name:
                return ticker

        return None

    return find_match

def load_ghgp_year(year):
    """Load GHGP data for a specific year."""
    file_path = SUMMARY_DIR / f"ghgp_data_{year}.xlsx"
    if not file_path.exists():
        return None

    df = pd.read_excel(file_path, header=3)
    df['year'] = year
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

    # Standardize key columns across years (column names vary slightly)
    rename_map = {}
    for col in df.columns:
        col_lower = str(col).lower()
        if 'facility' in col_lower and 'id' in col_lower and 'frs' not in col_lower:
            rename_map[col] = 'facility_id'
        elif 'facility' in col_lower and 'name' in col_lower:
            rename_map[col] = 'facility_name'
        elif 'total' in col_lower and 'emission' in col_lower and 'direct' in col_lower:
            rename_map[col] = 'total_emissions'
        elif 'naics' in col_lower:
            rename_map[col] = 'naics_code'
        elif col_lower == 'state':
            rename_map[col] = 'state'
        elif col_lower == 'latitude':
            rename_map[col] = 'latitude'
        elif col_lower == 'longitude':
            rename_map[col] = 'longitude'

    df = df.rename(columns=rename_map)

    # Keep only needed columns that exist
    keep_cols = ['facility_id', 'facility_name', 'total_emissions', 'naics_code',
                 'state', 'latitude', 'longitude', 'year']
    existing = [c for c in keep_cols if c in df.columns]
    df = df[existing].copy()

    # Clean facility ID
    df['facility_id'] = pd.to_numeric(df['facility_id'], errors='coerce')
    df = df.dropna(subset=['facility_id'])
    df['facility_id'] = df['facility_id'].astype(int)

    # Clean emissions
    df['total_emissions'] = pd.to_numeric(df['total_emissions'], errors='coerce')

    return df

def main():
    print("Processing EPA GHGRP data for all years...")
    print("=" * 60)

    # Load reference data
    print("\n1. Loading reference data...")
    sp500 = load_sp500()
    print(f"   S&P 500 companies: {len(sp500)}")

    parent_data = load_parent_company_data()
    print(f"   Parent company records (2023): {len(parent_data)}")

    # Build facility-to-parent lookup (using 2023 data)
    facility_parent = parent_data[['GHGRP FACILITY ID', 'PARENT COMPANY NAME',
                                    'PARENT CO. PERCENT OWNERSHIP', 'clean_parent']].copy()
    facility_parent.columns = ['facility_id', 'parent_company', 'ownership_pct', 'clean_parent']
    facility_parent = facility_parent.drop_duplicates(subset=['facility_id'])
    print(f"   Unique facilities with parent data: {len(facility_parent)}")

    # Build ticker matcher
    find_ticker = build_ticker_matcher(sp500)

    # Add ticker to facility lookup
    facility_parent['ticker'] = facility_parent['clean_parent'].apply(find_ticker)
    sp500_facilities = facility_parent[facility_parent['ticker'].notna()].copy()
    print(f"   Facilities matched to S&P 500: {len(sp500_facilities)}")
    print(f"   Unique S&P 500 tickers: {sp500_facilities['ticker'].nunique()}")

    # Load all years of GHGP data
    print("\n2. Loading GHGP data for all years...")
    all_years = []
    for year in range(2010, 2024):
        print(f"   Loading {year}...", end=" ")
        df = load_ghgp_year(year)
        if df is not None:
            print(f"{len(df)} facilities")
            all_years.append(df)
        else:
            print("skipped")

    ghgp_all = pd.concat(all_years, ignore_index=True)
    print(f"\n   Total facility-year records: {len(ghgp_all)}")

    # Merge with parent company data (using stable facility IDs)
    print("\n3. Merging with parent company data...")
    ghgp_all = ghgp_all.merge(facility_parent, on='facility_id', how='left')
    matched = ghgp_all['parent_company'].notna().sum()
    print(f"   Facility-years with parent company: {matched}")

    # Filter to S&P 500
    sp500_data = ghgp_all[ghgp_all['ticker'].notna()].copy()
    print(f"   Facility-years matched to S&P 500: {len(sp500_data)}")

    # Save facility-level data
    print("\n4. Saving processed data...")
    PROCESSED_DIR.mkdir(exist_ok=True)

    # All facilities (all years)
    ghgp_all.to_csv(PROCESSED_DIR / "ghgrp_facilities_all_years.csv", index=False)
    print(f"   Saved: ghgrp_facilities_all_years.csv ({len(ghgp_all)} records)")

    # S&P 500 facilities (all years)
    sp500_data.to_csv(PROCESSED_DIR / "ghgrp_facilities_sp500_all_years.csv", index=False)
    print(f"   Saved: ghgrp_facilities_sp500_all_years.csv ({len(sp500_data)} records)")

    # Aggregate to company-year level for S&P 500
    company_year = (sp500_data
        .groupby(['ticker', 'year'])
        .agg({
            'total_emissions': 'sum',
            'facility_id': 'count',
            'state': lambda x: x.mode().iloc[0] if len(x) > 0 and len(x.mode()) > 0 else None
        })
        .reset_index())
    company_year.columns = ['ticker', 'year', 'total_emissions', 'num_facilities', 'primary_state']
    company_year = company_year.sort_values(['ticker', 'year'])

    company_year.to_csv(PROCESSED_DIR / "ghgrp_company_year_sp500_all_years.csv", index=False)
    print(f"   Saved: ghgrp_company_year_sp500_all_years.csv ({len(company_year)} records)")

    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    years_present = sorted(company_year['year'].unique())
    print(f"\nYears covered: {min(years_present)}-{max(years_present)} ({len(years_present)} years)")
    print(f"S&P 500 companies with emissions data: {company_year['ticker'].nunique()}")
    print(f"Company-year observations: {len(company_year)}")

    print("\nCompanies by year:")
    year_counts = company_year.groupby('year')['ticker'].count()
    for year, count in year_counts.items():
        print(f"   {year}: {count} companies")

    print("\nTop 10 emitters (2023):")
    top_2023 = company_year[company_year['year'] == 2023].nlargest(10, 'total_emissions')
    for _, row in top_2023.iterrows():
        print(f"   {row['ticker']}: {row['total_emissions']:,.0f} metric tons CO2e")

    # Panel balance check
    print("\nPanel structure:")
    obs_per_firm = company_year.groupby('ticker')['year'].count()
    print(f"   Companies with all {len(years_present)} years: {(obs_per_firm == len(years_present)).sum()}")
    print(f"   Average years per company: {obs_per_firm.mean():.1f}")

    print("\n" + "=" * 60)
    print("Processing complete!")

if __name__ == "__main__":
    main()
