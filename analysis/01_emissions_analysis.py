"""
AI Adoption and ESG Trade-offs: Emissions Analysis
===================================================

Research Question: Does AI adoption create a productivity-ESG trade-off for public firms?

Key Event: ChatGPT launch (November 30, 2022) as exogenous shock to AI adoption pressure

Data: EPA GHGRP facility-level emissions (2010-2023) matched to S&P 500 companies
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up paths
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Plot settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

# =============================================================================
# 1. LOAD DATA
# =============================================================================
print("=" * 60)
print("LOADING DATA")
print("=" * 60)

# EPA GHGRP emissions panel
emissions = pd.read_csv(DATA_DIR / "epa_ghgrp/processed/ghgrp_company_year_sp500_all_years.csv")
print(f"\nEmissions panel: {len(emissions)} company-year observations")
print(f"  Companies: {emissions['ticker'].nunique()}")
print(f"  Years: {emissions['year'].min()}-{emissions['year'].max()}")

# S&P 500 constituents with sector info
sp500 = pd.read_csv(DATA_DIR / "sp500_constituents.csv")
print(f"\nS&P 500 list: {len(sp500)} companies")

# Merge sector information
emissions = emissions.merge(
    sp500[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry']],
    left_on='ticker', right_on='Symbol', how='left'
)

# =============================================================================
# 2. SUMMARY STATISTICS
# =============================================================================
print("\n" + "=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)

# Panel structure
print("\n--- Panel Structure ---")
obs_per_firm = emissions.groupby('ticker')['year'].count()
print(f"Mean years per firm: {obs_per_firm.mean():.1f}")
print(f"Firms with complete panel (14 years): {(obs_per_firm == 14).sum()}")

# Emissions summary by year
print("\n--- Total Emissions by Year (Million Metric Tons CO2e) ---")
yearly = emissions.groupby('year')['total_emissions'].agg(['sum', 'mean', 'count'])
yearly['sum'] = yearly['sum'] / 1e6
yearly['mean'] = yearly['mean'] / 1e6
yearly.columns = ['Total (M)', 'Mean (M)', 'N Firms']
print(yearly.to_string())

# Top emitters
print("\n--- Top 10 Emitters (2023) ---")
top_2023 = emissions[emissions['year'] == 2023].nlargest(10, 'total_emissions')
for _, row in top_2023.iterrows():
    print(f"  {row['ticker']:6} ({row['GICS Sector'][:20]:20}): {row['total_emissions']/1e6:8.2f} M tons")

# Emissions by sector
print("\n--- Emissions by GICS Sector (2023, Million Metric Tons) ---")
sector_2023 = emissions[emissions['year'] == 2023].groupby('GICS Sector')['total_emissions'].agg(['sum', 'mean', 'count'])
sector_2023['sum'] = sector_2023['sum'] / 1e6
sector_2023['mean'] = sector_2023['mean'] / 1e6
sector_2023 = sector_2023.sort_values('sum', ascending=False)
sector_2023.columns = ['Total (M)', 'Mean (M)', 'N Firms']
print(sector_2023.to_string())

# =============================================================================
# 3. PRE/POST CHATGPT ANALYSIS
# =============================================================================
print("\n" + "=" * 60)
print("PRE/POST CHATGPT ANALYSIS (Nov 2022)")
print("=" * 60)

# Define treatment periods
# Pre-period: 2019-2022 (4 years before ChatGPT)
# Post-period: 2023 (1 year after - limited data)
emissions['post_chatgpt'] = (emissions['year'] >= 2023).astype(int)
emissions['pre_period'] = emissions['year'].isin([2019, 2020, 2021, 2022]).astype(int)

# Calculate firm-level changes
pre_avg = emissions[emissions['year'].isin([2020, 2021, 2022])].groupby('ticker')['total_emissions'].mean()
post_avg = emissions[emissions['year'] == 2023].groupby('ticker')['total_emissions'].mean()

changes = pd.DataFrame({
    'pre_avg': pre_avg,
    'post_2023': post_avg
}).dropna()
changes['change'] = changes['post_2023'] - changes['pre_avg']
changes['pct_change'] = (changes['change'] / changes['pre_avg']) * 100

# Merge sector info
changes = changes.merge(
    emissions[['ticker', 'GICS Sector']].drop_duplicates(),
    left_index=True, right_on='ticker'
).set_index('ticker')

print(f"\nFirms with pre and post data: {len(changes)}")
print(f"\nEmissions Change (2020-2022 avg → 2023):")
print(f"  Mean change: {changes['pct_change'].mean():+.1f}%")
print(f"  Median change: {changes['pct_change'].median():+.1f}%")
print(f"  Firms with increased emissions: {(changes['change'] > 0).sum()} ({(changes['change'] > 0).mean()*100:.1f}%)")

# Changes by sector
print("\n--- Emissions Change by Sector (%) ---")
sector_changes = changes.groupby('GICS Sector')['pct_change'].agg(['mean', 'median', 'count'])
sector_changes = sector_changes.sort_values('mean', ascending=False)
sector_changes.columns = ['Mean %', 'Median %', 'N']
print(sector_changes.to_string())

# =============================================================================
# 4. IDENTIFY TECH/AI-INTENSIVE FIRMS
# =============================================================================
print("\n" + "=" * 60)
print("TECH SECTOR ANALYSIS")
print("=" * 60)

# Tech sectors likely to be AI adopters
tech_sectors = ['Information Technology', 'Communication Services']
tech_firms = emissions[emissions['GICS Sector'].isin(tech_sectors)]['ticker'].unique()
print(f"\nTech/Communication firms in sample: {len(tech_firms)}")

# Compare tech vs non-tech emissions trends
tech_yearly = emissions[emissions['GICS Sector'].isin(tech_sectors)].groupby('year')['total_emissions'].sum() / 1e6
nontech_yearly = emissions[~emissions['GICS Sector'].isin(tech_sectors)].groupby('year')['total_emissions'].sum() / 1e6

print("\n--- Tech vs Non-Tech Emissions (Million Metric Tons) ---")
comparison = pd.DataFrame({
    'Tech': tech_yearly,
    'Non-Tech': nontech_yearly
})
comparison['Tech_pct'] = comparison['Tech'] / (comparison['Tech'] + comparison['Non-Tech']) * 100
print(comparison.to_string())

# =============================================================================
# 5. VISUALIZATIONS
# =============================================================================
print("\n" + "=" * 60)
print("GENERATING VISUALIZATIONS")
print("=" * 60)

# Figure 1: Total emissions over time
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel A: Total emissions
ax1 = axes[0]
yearly_total = emissions.groupby('year')['total_emissions'].sum() / 1e6
ax1.plot(yearly_total.index, yearly_total.values, 'b-o', linewidth=2, markersize=6)
ax1.axvline(x=2022.92, color='red', linestyle='--', alpha=0.7, label='ChatGPT Launch')
ax1.set_xlabel('Year')
ax1.set_ylabel('Total Emissions (Million Metric Tons CO2e)')
ax1.set_title('A. Aggregate S&P 500 Emissions (GHGRP Reporters)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel B: By sector
ax2 = axes[1]
top_sectors = ['Utilities', 'Energy', 'Materials', 'Industrials']
for sector in top_sectors:
    sector_data = emissions[emissions['GICS Sector'] == sector].groupby('year')['total_emissions'].sum() / 1e6
    ax2.plot(sector_data.index, sector_data.values, '-o', linewidth=2, markersize=4, label=sector)
ax2.axvline(x=2022.92, color='red', linestyle='--', alpha=0.7)
ax2.set_xlabel('Year')
ax2.set_ylabel('Total Emissions (Million Metric Tons CO2e)')
ax2.set_title('B. Emissions by Sector')
ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig1_emissions_trends.png', dpi=150, bbox_inches='tight')
print(f"  Saved: fig1_emissions_trends.png")

# Figure 2: Pre/Post ChatGPT changes by sector
fig, ax = plt.subplots(figsize=(10, 6))
sector_order = sector_changes.sort_values('Mean %').index
colors = ['green' if x < 0 else 'red' for x in sector_changes.loc[sector_order, 'Mean %']]
bars = ax.barh(sector_order, sector_changes.loc[sector_order, 'Mean %'], color=colors, alpha=0.7)
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlabel('Mean % Change in Emissions (2020-22 avg → 2023)')
ax.set_title('Emissions Change by Sector After ChatGPT Launch')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig2_sector_changes.png', dpi=150, bbox_inches='tight')
print(f"  Saved: fig2_sector_changes.png")

# Figure 3: Distribution of firm-level changes
fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(changes['pct_change'].clip(-50, 50), bins=30, edgecolor='black', alpha=0.7)
ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
ax.axvline(x=changes['pct_change'].mean(), color='blue', linestyle='-', linewidth=2, label=f"Mean: {changes['pct_change'].mean():.1f}%")
ax.axvline(x=changes['pct_change'].median(), color='green', linestyle='-', linewidth=2, label=f"Median: {changes['pct_change'].median():.1f}%")
ax.set_xlabel('% Change in Emissions (2020-22 avg → 2023)')
ax.set_ylabel('Number of Firms')
ax.set_title('Distribution of Firm-Level Emissions Changes')
ax.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig3_change_distribution.png', dpi=150, bbox_inches='tight')
print(f"  Saved: fig3_change_distribution.png")

# Figure 4: Time series for top emitters
fig, ax = plt.subplots(figsize=(12, 6))
top_tickers = ['VST', 'DUK', 'SO', 'XOM', 'NEE']
for ticker in top_tickers:
    firm_data = emissions[emissions['ticker'] == ticker].set_index('year')['total_emissions'] / 1e6
    ax.plot(firm_data.index, firm_data.values, '-o', linewidth=2, markersize=4, label=ticker)
ax.axvline(x=2022.92, color='red', linestyle='--', alpha=0.7, label='ChatGPT')
ax.set_xlabel('Year')
ax.set_ylabel('Emissions (Million Metric Tons CO2e)')
ax.set_title('Emissions Trends: Top 5 Emitters')
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig4_top_emitters.png', dpi=150, bbox_inches='tight')
print(f"  Saved: fig4_top_emitters.png")

plt.close('all')

# =============================================================================
# 6. EXPORT ANALYSIS DATA
# =============================================================================
print("\n" + "=" * 60)
print("EXPORTING ANALYSIS DATA")
print("=" * 60)

# Export firm-level changes
changes.reset_index().to_csv(OUTPUT_DIR / 'firm_emissions_changes.csv', index=False)
print(f"  Saved: firm_emissions_changes.csv ({len(changes)} firms)")

# Export yearly summary
yearly_summary = emissions.groupby('year').agg({
    'total_emissions': ['sum', 'mean', 'std', 'count'],
    'num_facilities': 'sum'
}).round(2)
yearly_summary.columns = ['total_emissions', 'mean_emissions', 'std_emissions', 'n_firms', 'total_facilities']
yearly_summary.to_csv(OUTPUT_DIR / 'yearly_summary.csv')
print(f"  Saved: yearly_summary.csv")

# Export sector summary
sector_summary = emissions.groupby(['year', 'GICS Sector']).agg({
    'total_emissions': ['sum', 'mean', 'count']
}).round(2)
sector_summary.columns = ['total_emissions', 'mean_emissions', 'n_firms']
sector_summary.to_csv(OUTPUT_DIR / 'sector_year_summary.csv')
print(f"  Saved: sector_year_summary.csv")

# =============================================================================
# 7. SUMMARY
# =============================================================================
print("\n" + "=" * 60)
print("ANALYSIS SUMMARY")
print("=" * 60)

print("""
KEY FINDINGS:
1. Panel covers 121 S&P 500 firms with GHGRP emissions data (2010-2023)
2. Utilities and Energy sectors dominate emissions
3. Overall emissions trend: [see yearly summary above]

NEXT STEPS FOR DIFF-IN-DIFF ANALYSIS:
1. Construct AI exposure index from O*NET data (by industry)
2. Match firms to industry-level AI exposure scores
3. Define treatment: High AI exposure × Post-ChatGPT
4. Estimate: Emissions_it = β(HighExposure_i × Post_t) + FirmFE + YearFE + ε
5. Add controls: firm size, industry trends, regional grid carbon intensity

DATA LIMITATIONS:
- GHGRP only covers large emitters (>25,000 metric tons CO2e/year)
- Tech firms (FAANG) may not have direct GHGRP-reported facilities
- Parent company matching uses 2023 ownership data for all years
""")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
