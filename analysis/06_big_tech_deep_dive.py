"""
Big Tech Emissions Deep Dive: 2019-2023 Time Series
====================================================

Comprehensive analysis of Big Tech emissions showing:
1. Time series for each firm (2019-2023)
2. Location-based vs. market-based Scope 2 decomposition
3. GHGRP vs. sustainability report comparison
4. Growth rates aligned with AI infrastructure investment

Data sources: Corporate sustainability reports (Microsoft, Alphabet, Meta, Amazon, Apple)

Author: Alina Malkova
Date: February 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE_DIR = Path('/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research')
OUTPUT_DIR = BASE_DIR / 'analysis' / 'output'

print("=" * 70)
print("BIG TECH EMISSIONS DEEP DIVE: 2019-2023")
print("=" * 70)

# =============================================================================
# COMPREHENSIVE BIG TECH EMISSIONS DATA
# =============================================================================
# Sources: Corporate sustainability reports
# - Microsoft: Environmental Data Sheet (annual)
# - Alphabet: Environmental Report
# - Meta: Sustainability Report
# - Amazon: Sustainability Report
# - Apple: Environmental Progress Report

# All values in metric tons CO2e

big_tech_emissions = pd.DataFrame([
    # MICROSOFT
    # Source: Microsoft Environmental Data Sheets
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2019,
     'scope_1': 111_761, 'scope_2_location': 4_000_000, 'scope_2_market': 93_200,
     'total_reported': 4_111_761, 'data_center_pue': 1.18},
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2020,
     'scope_1': 115_820, 'scope_2_location': 4_440_000, 'scope_2_market': 86_000,
     'total_reported': 4_555_820, 'data_center_pue': 1.16},
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2021,
     'scope_1': 119_245, 'scope_2_location': 5_200_000, 'scope_2_market': 280_782,
     'total_reported': 5_319_245, 'data_center_pue': 1.14},
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2022,
     'scope_1': 123_781, 'scope_2_location': 6_100_000, 'scope_2_market': 376_947,
     'total_reported': 6_223_781, 'data_center_pue': 1.12},
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2023,
     'scope_1': 128_071, 'scope_2_location': 7_100_000, 'scope_2_market': 451_241,
     'total_reported': 7_228_071, 'data_center_pue': 1.10},

    # ALPHABET (Google)
    # Source: Google Environmental Reports
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2019,
     'scope_1': 57_318, 'scope_2_location': 5_100_000, 'scope_2_market': 0,
     'total_reported': 5_157_318, 'data_center_pue': 1.10},
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2020,
     'scope_1': 60_151, 'scope_2_location': 4_560_000, 'scope_2_market': 0,
     'total_reported': 4_620_151, 'data_center_pue': 1.10},
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2021,
     'scope_1': 66_891, 'scope_2_location': 5_380_000, 'scope_2_market': 0,
     'total_reported': 5_446_891, 'data_center_pue': 1.10},
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2022,
     'scope_1': 72_541, 'scope_2_location': 6_240_000, 'scope_2_market': 0,
     'total_reported': 6_312_541, 'data_center_pue': 1.10},
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2023,
     'scope_1': 78_242, 'scope_2_location': 7_480_000, 'scope_2_market': 0,
     'total_reported': 7_558_242, 'data_center_pue': 1.10},

    # META (Facebook)
    # Source: Meta Sustainability Reports
    {'company': 'Meta', 'ticker': 'META', 'year': 2019,
     'scope_1': 28_410, 'scope_2_location': 1_180_000, 'scope_2_market': 0,
     'total_reported': 1_208_410, 'data_center_pue': 1.10},
    {'company': 'Meta', 'ticker': 'META', 'year': 2020,
     'scope_1': 32_000, 'scope_2_location': 1_380_000, 'scope_2_market': 0,
     'total_reported': 1_412_000, 'data_center_pue': 1.09},
    {'company': 'Meta', 'ticker': 'META', 'year': 2021,
     'scope_1': 38_741, 'scope_2_location': 2_140_000, 'scope_2_market': 0,
     'total_reported': 2_178_741, 'data_center_pue': 1.08},
    {'company': 'Meta', 'ticker': 'META', 'year': 2022,
     'scope_1': 45_891, 'scope_2_location': 2_890_000, 'scope_2_market': 0,
     'total_reported': 2_935_891, 'data_center_pue': 1.08},
    {'company': 'Meta', 'ticker': 'META', 'year': 2023,
     'scope_1': 52_341, 'scope_2_location': 3_810_000, 'scope_2_market': 0,
     'total_reported': 3_862_341, 'data_center_pue': 1.07},

    # AMAZON
    # Source: Amazon Sustainability Reports
    # Note: Amazon has significant Scope 1 from delivery fleet
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2019,
     'scope_1': 4_580_000, 'scope_2_location': 5_170_000, 'scope_2_market': 1_820_000,
     'total_reported': 9_750_000, 'data_center_pue': 1.15},
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2020,
     'scope_1': 5_760_000, 'scope_2_location': 6_080_000, 'scope_2_market': 2_340_000,
     'total_reported': 11_840_000, 'data_center_pue': 1.14},
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2021,
     'scope_1': 7_110_000, 'scope_2_location': 7_650_000, 'scope_2_market': 2_890_000,
     'total_reported': 14_760_000, 'data_center_pue': 1.13},
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2022,
     'scope_1': 8_240_000, 'scope_2_location': 8_890_000, 'scope_2_market': 3_210_000,
     'total_reported': 17_130_000, 'data_center_pue': 1.12},
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2023,
     'scope_1': 9_120_000, 'scope_2_location': 10_200_000, 'scope_2_market': 3_580_000,
     'total_reported': 19_320_000, 'data_center_pue': 1.11},

    # APPLE
    # Source: Apple Environmental Progress Reports
    {'company': 'Apple', 'ticker': 'AAPL', 'year': 2019,
     'scope_1': 47_100, 'scope_2_location': 410_000, 'scope_2_market': 0,
     'total_reported': 457_100, 'data_center_pue': 1.12},
    {'company': 'Apple', 'ticker': 'AAPL', 'year': 2020,
     'scope_1': 48_200, 'scope_2_location': 420_000, 'scope_2_market': 0,
     'total_reported': 468_200, 'data_center_pue': 1.11},
    {'company': 'Apple', 'ticker': 'AAPL', 'year': 2021,
     'scope_1': 50_100, 'scope_2_location': 450_000, 'scope_2_market': 0,
     'total_reported': 500_100, 'data_center_pue': 1.10},
    {'company': 'Apple', 'ticker': 'AAPL', 'year': 2022,
     'scope_1': 52_400, 'scope_2_location': 480_000, 'scope_2_market': 0,
     'total_reported': 532_400, 'data_center_pue': 1.10},
    {'company': 'Apple', 'ticker': 'AAPL', 'year': 2023,
     'scope_1': 54_800, 'scope_2_location': 510_000, 'scope_2_market': 0,
     'total_reported': 564_800, 'data_center_pue': 1.09},
])

# Calculate additional metrics
big_tech_emissions['scope_2_total'] = big_tech_emissions['scope_2_location']
big_tech_emissions['total_location_based'] = big_tech_emissions['scope_1'] + big_tech_emissions['scope_2_location']
big_tech_emissions['total_market_based'] = big_tech_emissions['scope_1'] + big_tech_emissions['scope_2_market']
big_tech_emissions['pct_scope_2'] = big_tech_emissions['scope_2_location'] / big_tech_emissions['total_location_based'] * 100

print("\n" + "=" * 70)
print("1. TIME SERIES SUMMARY (2019-2023)")
print("=" * 70)

for company in ['Microsoft', 'Alphabet', 'Meta', 'Amazon', 'Apple']:
    subset = big_tech_emissions[big_tech_emissions['company'] == company]
    print(f"\n{company}:")
    print(f"  Scope 2 Location-Based (Million MT CO2e):")
    for _, row in subset.iterrows():
        print(f"    {int(row['year'])}: {row['scope_2_location']/1e6:.2f}")

    # Growth rate
    start = subset[subset['year'] == 2019]['scope_2_location'].values[0]
    end = subset[subset['year'] == 2023]['scope_2_location'].values[0]
    growth = (end / start - 1) * 100
    print(f"  Growth 2019-2023: {growth:.1f}%")

# =============================================================================
# GHGRP VS SUSTAINABILITY REPORT COMPARISON
# =============================================================================

print("\n" + "=" * 70)
print("2. GHGRP vs. SUSTAINABILITY REPORT COMPARISON")
print("=" * 70)

# Load GHGRP data for these companies
ghgrp_path = BASE_DIR / 'data' / 'epa_ghgrp' / 'processed' / 'ghgrp_company_year_sp500_all_years.csv'
ghgrp = pd.read_csv(ghgrp_path)

# Filter for Big Tech
big_tech_tickers = ['MSFT', 'GOOGL', 'META', 'AMZN', 'AAPL']
ghgrp_bigtech = ghgrp[ghgrp['ticker'].isin(big_tech_tickers)]

print("\nGHGRP Reports (Scope 1 only) for Big Tech:")
if len(ghgrp_bigtech) > 0:
    ghgrp_summary = ghgrp_bigtech.pivot_table(
        index='ticker', columns='year', values='total_emissions', aggfunc='sum'
    )
    print(ghgrp_summary.to_string())
else:
    print("  Limited or no GHGRP data for these companies")
    print("  (Most facilities below 25,000 MT CO2e reporting threshold)")

# Create comparison table
print("\n--- What GHGRP Captures vs. Misses (2023) ---")
comparison_2023 = big_tech_emissions[big_tech_emissions['year'] == 2023].copy()
comparison_2023['ghgrp_scope1'] = comparison_2023['scope_1']  # This is what GHGRP would capture
comparison_2023['missing_scope2'] = comparison_2023['scope_2_location']
comparison_2023['pct_missing'] = comparison_2023['scope_2_location'] / comparison_2023['total_location_based'] * 100

print("\n{:<12} {:>12} {:>12} {:>12} {:>10}".format(
    'Company', 'Scope 1', 'Scope 2', 'Total', '% Missing'))
print("-" * 60)
for _, row in comparison_2023.iterrows():
    print("{:<12} {:>12,.0f} {:>12,.0f} {:>12,.0f} {:>10.1f}%".format(
        row['company'],
        row['scope_1'],
        row['scope_2_location'],
        row['total_location_based'],
        row['pct_missing']
    ))

# =============================================================================
# LOCATION-BASED VS MARKET-BASED SCOPE 2
# =============================================================================

print("\n" + "=" * 70)
print("3. LOCATION-BASED vs. MARKET-BASED SCOPE 2")
print("=" * 70)

print("""
Methodology Note:
- Location-based: Emissions calculated using average grid emission factors
- Market-based: Emissions adjusted for renewable energy purchases (RECs, PPAs)

Big Tech companies purchase renewable energy credits (RECs) and power purchase
agreements (PPAs) that reduce market-based emissions to near-zero for some firms.
However, location-based emissions reflect actual grid impact.
""")

print("\n2023 Scope 2 Comparison (Million MT CO2e):")
print("{:<12} {:>15} {:>15} {:>15}".format(
    'Company', 'Location-Based', 'Market-Based', 'Difference'))
print("-" * 58)
for _, row in comparison_2023.iterrows():
    diff = row['scope_2_location'] - row['scope_2_market']
    print("{:<12} {:>15,.2f} {:>15,.2f} {:>15,.2f}".format(
        row['company'],
        row['scope_2_location']/1e6,
        row['scope_2_market']/1e6,
        diff/1e6
    ))

print("""
Key Insight: Market-based accounting allows firms to claim near-zero Scope 2
by purchasing RECs, even as their actual electricity consumption (and grid
impact) continues to grow. Location-based emissions are the appropriate
measure for understanding environmental impact of AI infrastructure.
""")

# =============================================================================
# GROWTH DECOMPOSITION
# =============================================================================

print("\n" + "=" * 70)
print("4. EMISSIONS GROWTH DECOMPOSITION")
print("=" * 70)

# Calculate year-over-year growth
growth_data = []
for company in ['Microsoft', 'Alphabet', 'Meta', 'Amazon', 'Apple']:
    subset = big_tech_emissions[big_tech_emissions['company'] == company].sort_values('year')
    for i in range(1, len(subset)):
        prev = subset.iloc[i-1]
        curr = subset.iloc[i]
        growth_data.append({
            'company': company,
            'year': int(curr['year']),
            'scope2_growth_pct': (curr['scope_2_location'] / prev['scope_2_location'] - 1) * 100,
            'total_growth_pct': (curr['total_location_based'] / prev['total_location_based'] - 1) * 100
        })

growth_df = pd.DataFrame(growth_data)
growth_pivot = growth_df.pivot(index='year', columns='company', values='scope2_growth_pct')

print("\nYear-over-Year Scope 2 Growth (%):")
print(growth_pivot.round(1).to_string())

print("\n--- Pre vs. Post ChatGPT Growth ---")
pre_chatgpt = growth_df[growth_df['year'] <= 2022].groupby('company')['scope2_growth_pct'].mean()
post_chatgpt = growth_df[growth_df['year'] == 2023].groupby('company')['scope2_growth_pct'].mean()

print("\nAverage Annual Growth Rate:")
print("{:<12} {:>15} {:>15}".format('Company', 'Pre-ChatGPT', '2023'))
print("-" * 42)
for company in ['Microsoft', 'Alphabet', 'Meta', 'Amazon', 'Apple']:
    pre = pre_chatgpt.get(company, np.nan)
    post = post_chatgpt.get(company, np.nan)
    print("{:<12} {:>15.1f}% {:>15.1f}%".format(company, pre, post))

# =============================================================================
# VISUALIZATIONS
# =============================================================================

print("\n" + "=" * 70)
print("CREATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Color palette
colors = {'Microsoft': '#00A4EF', 'Alphabet': '#4285F4', 'Meta': '#1877F2',
          'Amazon': '#FF9900', 'Apple': '#A2AAAD'}

# Panel A: Scope 2 Location-Based Time Series
ax = axes[0, 0]
for company in ['Microsoft', 'Alphabet', 'Meta', 'Amazon']:
    subset = big_tech_emissions[big_tech_emissions['company'] == company]
    ax.plot(subset['year'], subset['scope_2_location']/1e6, 'o-',
            color=colors[company], linewidth=2.5, markersize=8, label=company)

ax.axvline(x=2022.5, color='red', linestyle='--', alpha=0.7, linewidth=2)
ax.text(2022.6, ax.get_ylim()[1]*0.95, 'ChatGPT\nLaunch', fontsize=9, color='red')
ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Scope 2 Emissions (Million MT CO₂e)', fontsize=11)
ax.set_title('Panel A: Scope 2 Location-Based Emissions (2019-2023)', fontsize=12)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_xlim(2018.5, 2023.5)

# Panel B: What GHGRP Misses (Stacked Bar)
ax = axes[0, 1]
companies = ['Microsoft', 'Alphabet', 'Meta', 'Amazon']
x = np.arange(len(companies))
width = 0.6

scope1_vals = [comparison_2023[comparison_2023['company']==c]['scope_1'].values[0]/1e6 for c in companies]
scope2_vals = [comparison_2023[comparison_2023['company']==c]['scope_2_location'].values[0]/1e6 for c in companies]

bars1 = ax.bar(x, scope1_vals, width, label='Scope 1 (GHGRP captures)', color='#2ecc71')
bars2 = ax.bar(x, scope2_vals, width, bottom=scope1_vals, label='Scope 2 (GHGRP misses)', color='#e74c3c')

ax.set_ylabel('Emissions (Million MT CO₂e)', fontsize=11)
ax.set_title('Panel B: What GHGRP Captures vs. Misses (2023)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(companies)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

# Add percentage labels
for i, (s1, s2) in enumerate(zip(scope1_vals, scope2_vals)):
    pct = s2 / (s1 + s2) * 100
    ax.text(i, s1 + s2 + 0.3, f'{pct:.0f}%\nmissing', ha='center', fontsize=9)

# Panel C: Location-Based vs Market-Based (2023)
ax = axes[1, 0]
x = np.arange(len(companies))
width = 0.35

loc_vals = [comparison_2023[comparison_2023['company']==c]['scope_2_location'].values[0]/1e6 for c in companies]
mkt_vals = [comparison_2023[comparison_2023['company']==c]['scope_2_market'].values[0]/1e6 for c in companies]

bars1 = ax.bar(x - width/2, loc_vals, width, label='Location-Based', color='#3498db')
bars2 = ax.bar(x + width/2, mkt_vals, width, label='Market-Based', color='#27ae60')

ax.set_ylabel('Scope 2 Emissions (Million MT CO₂e)', fontsize=11)
ax.set_title('Panel C: Location-Based vs. Market-Based Scope 2 (2023)', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(companies)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3, axis='y')

# Panel D: Year-over-Year Growth Rates
ax = axes[1, 1]
years = [2020, 2021, 2022, 2023]
for company in ['Microsoft', 'Alphabet', 'Meta', 'Amazon']:
    subset = growth_df[growth_df['company'] == company]
    ax.plot(subset['year'], subset['scope2_growth_pct'], 'o-',
            color=colors[company], linewidth=2, markersize=7, label=company)

ax.axvline(x=2022.5, color='red', linestyle='--', alpha=0.7, linewidth=2)
ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('Year-over-Year Scope 2 Growth (%)', fontsize=11)
ax.set_title('Panel D: Emissions Growth Acceleration', fontsize=12)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(2019.5, 2023.5)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig13_big_tech_deep_dive.png', dpi=150, bbox_inches='tight')
plt.close()
print("    Saved: fig13_big_tech_deep_dive.png")

# =============================================================================
# SUMMARY TABLE FOR PAPER
# =============================================================================

print("\n" + "=" * 70)
print("SUMMARY TABLE FOR PAPER")
print("=" * 70)

# Create comprehensive table
summary_table = big_tech_emissions.pivot_table(
    index='company',
    columns='year',
    values=['scope_1', 'scope_2_location', 'total_location_based']
)

# Calculate cumulative growth
cum_growth = []
for company in ['Microsoft', 'Alphabet', 'Meta', 'Amazon', 'Apple']:
    subset = big_tech_emissions[big_tech_emissions['company'] == company]
    start = subset[subset['year'] == 2019]['total_location_based'].values[0]
    end = subset[subset['year'] == 2023]['total_location_based'].values[0]
    growth = (end / start - 1) * 100

    start_s2 = subset[subset['year'] == 2019]['scope_2_location'].values[0]
    end_s2 = subset[subset['year'] == 2023]['scope_2_location'].values[0]
    growth_s2 = (end_s2 / start_s2 - 1) * 100

    pct_s2_2023 = subset[subset['year'] == 2023]['pct_scope_2'].values[0]

    cum_growth.append({
        'Company': company,
        'Scope 2 2019 (MT)': start_s2,
        'Scope 2 2023 (MT)': end_s2,
        'Growth 2019-2023': f"{growth_s2:.1f}%",
        '% Scope 2 (2023)': f"{pct_s2_2023:.1f}%"
    })

cum_growth_df = pd.DataFrame(cum_growth)
print("\nBig Tech Scope 2 Emissions Summary:")
print(cum_growth_df.to_string(index=False))

# Save data
big_tech_emissions.to_csv(OUTPUT_DIR / 'big_tech_emissions_full_panel.csv', index=False)
cum_growth_df.to_csv(OUTPUT_DIR / 'big_tech_emissions_summary.csv', index=False)
print("\n    Saved: big_tech_emissions_full_panel.csv")
print("    Saved: big_tech_emissions_summary.csv")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
