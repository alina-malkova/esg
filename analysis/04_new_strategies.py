"""
New Analysis Strategies for AI-ESG Trade-off Research
======================================================

Strategy 1: ESG Score Changes + AI Adoption Intensity (Panel)
Strategy 2: Utility-level Electricity Demand around Tech Hubs
Strategy 3: Investor Pricing of the Trade-off
Strategy 4: Builder vs. User Decomposition

Author: Alina Malkova
Date: February 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import statsmodels.api as sm
from statsmodels.formula.api import ols
import warnings
warnings.filterwarnings('ignore')

# Set paths
BASE_DIR = Path('/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research')
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'analysis' / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')

print("=" * 70)
print("NEW ANALYSIS STRATEGIES FOR AI-ESG TRADE-OFF")
print("=" * 70)

# =============================================================================
# LOAD EXISTING DATA
# =============================================================================

print("\n[1] Loading existing datasets...")

# S&P 500 constituents
sp500 = pd.read_csv(DATA_DIR / 'sp500_constituents.csv')
sp500 = sp500.rename(columns={'Symbol': 'ticker', 'Security': 'company', 'GICS Sector': 'GICS_sector'})
print(f"    S&P 500 companies: {len(sp500)}")

# AI exposure index
ai_exposure = pd.read_csv(OUTPUT_DIR / 'ai_exposure_by_sector.csv')
print(f"    AI exposure by sector: {len(ai_exposure)} sectors")

# GHGRP emissions panel
ghgrp = pd.read_csv(DATA_DIR / 'epa_ghgrp' / 'processed' / 'ghgrp_company_year_sp500_all_years.csv')
print(f"    GHGRP panel: {len(ghgrp)} company-year obs")

# Stock data
stock_files = list((DATA_DIR / 'stocks').glob('*_prices.csv'))
print(f"    Stock price files: {len(stock_files)}")

# Ken French factors
ff_factors = pd.read_csv(DATA_DIR / 'ken_french' / 'F-F_Research_Data_Factors_daily.csv', skiprows=3)
print(f"    Fama-French factors loaded")

# =============================================================================
# STRATEGY 4: BUILDER VS. USER DECOMPOSITION
# =============================================================================

print("\n" + "=" * 70)
print("STRATEGY 4: BUILDER VS. USER DECOMPOSITION")
print("=" * 70)

# Define AI infrastructure builders vs. users
# Builders: hyperscalers, cloud providers, chip manufacturers, data center REITs
builders = [
    # Hyperscalers / Cloud
    'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'ORCL', 'IBM', 'CRM',
    # Semiconductors / Chips
    'NVDA', 'AMD', 'INTC', 'AVGO', 'QCOM', 'TXN', 'MU', 'MRVL', 'ADI', 'NXPI',
    # Data Center REITs
    'EQIX', 'DLR', 'AMT', 'CCI', 'SBAC',
    # Networking / Infrastructure
    'CSCO', 'ANET', 'JNPR',
    # Cloud Infrastructure
    'NOW', 'SNOW', 'DDOG', 'NET', 'MDB', 'PLTR'
]

# Users: firms that adopt AI for operations but don't build infrastructure
# High AI exposure sectors that are NOT builders
user_sectors = ['Financials', 'Health Care', 'Consumer Discretionary', 'Communication Services']

# Classify S&P 500 firms
sp500['is_builder'] = sp500['ticker'].isin(builders)
sp500['is_user'] = (sp500['GICS_sector'].isin(user_sectors)) & (~sp500['is_builder'])

print(f"\nClassification of S&P 500 firms:")
print(f"    AI Infrastructure Builders: {sp500['is_builder'].sum()}")
print(f"    AI Users (high-exposure non-builders): {sp500['is_user'].sum()}")
print(f"    Other firms: {(~sp500['is_builder'] & ~sp500['is_user']).sum()}")

# Merge with GHGRP
ghgrp_classified = ghgrp.merge(
    sp500[['ticker', 'is_builder', 'is_user', 'GICS_sector']],
    on='ticker',
    how='left'
)

# Fill missing classifications
ghgrp_classified['is_builder'] = ghgrp_classified['is_builder'].fillna(False)
ghgrp_classified['is_user'] = ghgrp_classified['is_user'].fillna(False)

print(f"\nGHGRP panel by classification:")
print(f"    Builder obs: {ghgrp_classified['is_builder'].sum()}")
print(f"    User obs: {ghgrp_classified['is_user'].sum()}")

# Create treatment variables
ghgrp_classified['post'] = (ghgrp_classified['year'] >= 2023).astype(int)
ghgrp_classified['log_emissions'] = np.log(ghgrp_classified['total_emissions'] + 1)

# Run separate DiD for builders vs users
print("\n--- DiD Results: Builders vs. Users ---")

for group, label in [(True, 'Builders'), (False, 'Users')]:
    if label == 'Builders':
        subset = ghgrp_classified[ghgrp_classified['is_builder']]
    else:
        subset = ghgrp_classified[ghgrp_classified['is_user']]

    if len(subset) > 20:
        # Simple pre-post comparison
        pre = subset[subset['year'] < 2023]['log_emissions'].mean()
        post = subset[subset['year'] >= 2023]['log_emissions'].mean()
        change = post - pre
        print(f"\n{label}:")
        print(f"    N obs: {len(subset)}")
        print(f"    Pre-2023 mean log emissions: {pre:.3f}")
        print(f"    Post-2023 mean log emissions: {post:.3f}")
        print(f"    Change: {change:+.3f} ({(np.exp(change)-1)*100:+.1f}%)")

# =============================================================================
# STRATEGY 2: UTILITY-LEVEL ELECTRICITY DEMAND AROUND TECH HUBS
# =============================================================================

print("\n" + "=" * 70)
print("STRATEGY 2: UTILITY ELECTRICITY DEMAND (EIA FORM 861)")
print("=" * 70)

# Define major data center corridors
tech_hub_states = {
    'VA': 'Northern Virginia (Loudoun County - largest data center market)',
    'OR': 'Central Oregon (The Dalles - Google, Meta)',
    'TX': 'Dallas-Fort Worth metro',
    'AZ': 'Phoenix metro (Salt River Project)',
    'NV': 'Reno/Las Vegas (Switch, Apple)',
    'NC': 'Research Triangle (Google, Apple)',
    'IA': 'Des Moines (Microsoft, Meta, Google)',
    'SC': 'Upstate (Google)',
    'GA': 'Atlanta metro (Google, Microsoft)',
    'OH': 'Columbus (Amazon, Google, Meta)'
}

non_hub_states = ['MT', 'WY', 'VT', 'ME', 'WV', 'NM', 'SD', 'ND', 'AK', 'HI']

print("\nData Center Hub States:")
for state, desc in tech_hub_states.items():
    print(f"    {state}: {desc}")

# Check if we have EIA 861 data
eia_path = DATA_DIR / 'eia_861'
if not eia_path.exists():
    print("\n*** EIA Form 861 data not yet downloaded ***")
    print("    Download from: https://www.eia.gov/electricity/data/eia861/")
    print("    Files needed: Sales_Ult_Cust_*.xlsx (2018-2024)")

    # Create download instructions
    eia_path.mkdir(exist_ok=True)
    with open(eia_path / 'DOWNLOAD_INSTRUCTIONS.txt', 'w') as f:
        f.write("""EIA Form 861 Data Download Instructions
========================================

1. Go to: https://www.eia.gov/electricity/data/eia861/

2. Download "Zip file" for each year (2018-2024)
   - Contains Sales to Ultimate Customers data
   - Utility-level electricity sales by state and customer class

3. Key files needed:
   - Sales_Ult_Cust_YYYY.xlsx (or .xls)

4. Data fields:
   - Utility Number, Utility Name, State
   - Residential, Commercial, Industrial sales (MWh)
   - Total sales and revenues

5. Analysis plan:
   - Compare electricity demand growth in tech hub states vs. non-hub states
   - Pre-period: 2018-2022, Post-period: 2023-2024
   - Treatment: States with major data center corridors
   - Control: States without significant data center presence

6. Alternative: Use EIA-923 for monthly generation data at power plant level
   https://www.eia.gov/electricity/data/eia923/
""")
    print(f"    Instructions saved to: {eia_path / 'DOWNLOAD_INSTRUCTIONS.txt'}")

else:
    print("\nProcessing EIA 861 data...")
    # Process would go here

# =============================================================================
# STRATEGY 3: INVESTOR PRICING OF THE TRADE-OFF
# =============================================================================

print("\n" + "=" * 70)
print("STRATEGY 3: INVESTOR PRICING OF THE TRADE-OFF")
print("=" * 70)

# Load stock data for tech firms
print("\nLoading stock price data...")

stock_data = []
for f in stock_files:
    ticker = f.stem.replace('_prices', '')
    df = pd.read_csv(f)
    df['ticker'] = ticker
    stock_data.append(df)

if stock_data:
    stocks = pd.concat(stock_data, ignore_index=True)
    stocks['Date'] = pd.to_datetime(stocks['Date'], errors='coerce', utc=True)
    stocks = stocks.dropna(subset=['Date'])
    stocks['year'] = stocks['Date'].dt.year
    stocks['month'] = stocks['Date'].dt.month

    print(f"    Stock data loaded: {len(stocks)} observations")
    print(f"    Tickers: {stocks['ticker'].unique()}")

    # Calculate returns
    stocks = stocks.sort_values(['ticker', 'Date'])
    stocks['return'] = stocks.groupby('ticker')['Close'].pct_change()

    # Mark pre/post ChatGPT
    chatgpt_date = pd.Timestamp('2022-11-30', tz='UTC')
    stocks['post_chatgpt'] = (stocks['Date'] > chatgpt_date).astype(int)

    # Calculate cumulative returns
    pre_chatgpt = stocks[stocks['Date'] <= chatgpt_date].groupby('ticker')['Close'].last()
    post_chatgpt = stocks[stocks['Date'] > chatgpt_date].groupby('ticker')['Close'].last()

    cum_returns = pd.DataFrame({
        'price_pre': pre_chatgpt,
        'price_post': post_chatgpt
    })
    cum_returns['cum_return'] = (cum_returns['price_post'] / cum_returns['price_pre'] - 1) * 100

    print("\nCumulative Returns Since ChatGPT Launch (Nov 30, 2022):")
    for ticker in cum_returns.index:
        ret = cum_returns.loc[ticker, 'cum_return']
        print(f"    {ticker}: {ret:+.1f}%")

# Manual Big Tech emissions data for pricing analysis
big_tech_data = pd.DataFrame([
    # 2020 baseline
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2020,
     'scope_1': 115_820, 'scope_2': 4_440_000, 'total': 4_555_820},
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2020,
     'scope_1': 60_151, 'scope_2': 4_560_000, 'total': 4_620_151},
    {'company': 'Meta', 'ticker': 'META', 'year': 2020,
     'scope_1': 32_000, 'scope_2': 1_380_000, 'total': 1_412_000},
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2020,
     'scope_1': 5_760_000, 'scope_2': 6_080_000, 'total': 11_840_000},

    # 2023 latest
    {'company': 'Microsoft', 'ticker': 'MSFT', 'year': 2023,
     'scope_1': 128_071, 'scope_2': 7_100_000, 'total': 7_228_071},
    {'company': 'Alphabet', 'ticker': 'GOOGL', 'year': 2023,
     'scope_1': 78_242, 'scope_2': 7_480_000, 'total': 7_558_242},
    {'company': 'Meta', 'ticker': 'META', 'year': 2023,
     'scope_1': 52_341, 'scope_2': 3_810_000, 'total': 3_862_341},
    {'company': 'Amazon', 'ticker': 'AMZN', 'year': 2023,
     'scope_1': 9_120_000, 'scope_2': 10_200_000, 'total': 19_320_000},
])

# Calculate emissions growth
emissions_growth = big_tech_data.pivot(index='ticker', columns='year', values='total')
emissions_growth['emissions_growth_pct'] = (emissions_growth[2023] / emissions_growth[2020] - 1) * 100

print("\n--- Big Tech Emissions Growth vs. Stock Returns ---")
print("\nEmissions Growth 2020-2023:")
for idx in emissions_growth.index:
    growth = emissions_growth.loc[idx, 'emissions_growth_pct']
    print(f"    {idx}: {growth:+.1f}%")

# Merge with stock returns if available
if stock_data and 'cum_returns' in dir():
    comparison = emissions_growth[['emissions_growth_pct']].join(cum_returns[['cum_return']])
    comparison = comparison.dropna()

    if len(comparison) > 2:
        print("\nEmissions Growth vs. Stock Returns Comparison:")
        print(comparison.round(1))

        # Correlation
        corr = comparison['emissions_growth_pct'].corr(comparison['cum_return'])
        print(f"\nCorrelation (emissions growth vs stock return): {corr:.3f}")
        print("    Interpretation: Positive = markets 'forgiving' emissions growth")

# =============================================================================
# STRATEGY 1: ESG SCORE DECOMPOSITION
# =============================================================================

print("\n" + "=" * 70)
print("STRATEGY 1: ESG SCORE DECOMPOSITION (E, S, G PILLARS)")
print("=" * 70)

# Check for ESG data availability
print("\nESG Data Status:")
print("    - Yahoo Finance ESG API: Deprecated/Restricted")
print("    - MSCI ESG Ratings: Commercial subscription required")
print("    - Sustainalytics: Commercial subscription required")
print("    - S&P Global ESG: Partial free access")

# Create a framework for when ESG data is available
print("\n--- Predicted 'Scissors' Pattern ---")
print("""
For firms with high AI adoption intensity:

    E (Environmental) Pillar:
        - Prediction: DETERIORATION
        - Mechanism: Increased energy consumption from data centers
        - Scope 2 emissions from electricity purchases

    S (Social) Pillar:
        - Prediction: MIXED/IMPROVEMENT
        - Mechanism: Potential job displacement offset by...
        - Better customer service, accessibility improvements

    G (Governance) Pillar:
        - Prediction: IMPROVEMENT
        - Mechanism: AI-powered compliance monitoring
        - Better risk management, fraud detection

    Net ESG Score:
        - May be stable or even improve, masking E deterioration
        - Decomposition is essential to reveal the trade-off
""")

# If we had ESG data, the analysis would look like:
print("\n--- Proposed Regression Framework ---")
print("""
Model: E_Score_Change_{it} = β₁(AI_Adoption_{it}) + β₂(Post_t)
                            + β₃(AI_Adoption_{it} × Post_t)
                            + α_i + γ_t + ε_{it}

Where:
    - AI_Adoption: Earnings call AI mentions, AI job postings, or AI patents
    - Post: Indicator for post-ChatGPT period (Nov 2022+)
    - α_i: Firm fixed effects
    - γ_t: Year fixed effects

Expected signs:
    - β₃ < 0 for E pillar (deterioration)
    - β₃ > 0 for S pillar (improvement)
    - β₃ > 0 for G pillar (improvement)
""")

# =============================================================================
# CREATE VISUALIZATIONS
# =============================================================================

print("\n" + "=" * 70)
print("CREATING VISUALIZATIONS")
print("=" * 70)

# Figure 9: Builder vs User Emissions Trajectories
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel A: Emissions over time by classification
for ax_idx, (is_builder, label, color) in enumerate([
    (True, 'AI Infrastructure Builders', 'crimson'),
    (False, 'AI Users', 'steelblue')
]):
    if label == 'AI Infrastructure Builders':
        subset = ghgrp_classified[ghgrp_classified['is_builder']]
    else:
        subset = ghgrp_classified[ghgrp_classified['is_user']]

    yearly = subset.groupby('year')['log_emissions'].agg(['mean', 'std', 'count'])
    yearly['se'] = yearly['std'] / np.sqrt(yearly['count'])

    axes[0].plot(yearly.index, yearly['mean'], 'o-', color=color,
                 label=label, linewidth=2, markersize=6)
    axes[0].fill_between(yearly.index,
                         yearly['mean'] - 1.96*yearly['se'],
                         yearly['mean'] + 1.96*yearly['se'],
                         alpha=0.2, color=color)

axes[0].axvline(x=2022.5, color='gray', linestyle='--', alpha=0.7, label='ChatGPT Launch')
axes[0].set_xlabel('Year', fontsize=12)
axes[0].set_ylabel('Mean Log Emissions', fontsize=12)
axes[0].set_title('Panel A: Emissions Trajectories by Firm Type', fontsize=12)
axes[0].legend(loc='upper right')
axes[0].set_xlim(2010, 2024)

# Panel B: Big Tech emissions growth vs stock returns
if stock_data and 'comparison' in dir() and len(comparison) > 0:
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for i, (ticker, row) in enumerate(comparison.iterrows()):
        axes[1].scatter(row['emissions_growth_pct'], row['cum_return'],
                       s=200, c=colors[i % len(colors)], label=ticker, zorder=5)

    # Add trend line if enough points
    if len(comparison) >= 3:
        z = np.polyfit(comparison['emissions_growth_pct'], comparison['cum_return'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(comparison['emissions_growth_pct'].min() - 10,
                            comparison['emissions_growth_pct'].max() + 10, 100)
        axes[1].plot(x_line, p(x_line), '--', color='gray', alpha=0.7, label='Trend')

    axes[1].set_xlabel('Emissions Growth 2020-2023 (%)', fontsize=12)
    axes[1].set_ylabel('Stock Return Since ChatGPT (%)', fontsize=12)
    axes[1].set_title('Panel B: Emissions Growth vs. Stock Returns', fontsize=12)
    axes[1].legend(loc='best')
    axes[1].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[1].axvline(x=0, color='black', linestyle='-', alpha=0.3)
else:
    axes[1].text(0.5, 0.5, 'Stock data not available\nfor all Big Tech firms',
                ha='center', va='center', fontsize=12, transform=axes[1].transAxes)
    axes[1].set_title('Panel B: Emissions Growth vs. Stock Returns', fontsize=12)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig9_builder_vs_user.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"    Saved: fig9_builder_vs_user.png")

# Figure 10: Predicted ESG Scissors Pattern (Conceptual)
fig, ax = plt.subplots(figsize=(10, 6))

years = np.arange(2018, 2027)
chatgpt_idx = 4  # 2022

# Simulated patterns for high AI adopters
e_score = np.concatenate([
    np.linspace(70, 72, chatgpt_idx + 1),  # Pre: slight improvement
    np.linspace(72, 58, len(years) - chatgpt_idx - 1)  # Post: deterioration
])

s_score = np.concatenate([
    np.linspace(65, 66, chatgpt_idx + 1),  # Pre: flat
    np.linspace(66, 74, len(years) - chatgpt_idx - 1)  # Post: improvement
])

g_score = np.concatenate([
    np.linspace(68, 69, chatgpt_idx + 1),  # Pre: flat
    np.linspace(69, 78, len(years) - chatgpt_idx - 1)  # Post: improvement
])

ax.plot(years, e_score, 'o-', color='forestgreen', linewidth=2.5,
        markersize=8, label='E (Environmental)')
ax.plot(years, s_score, 's-', color='royalblue', linewidth=2.5,
        markersize=8, label='S (Social)')
ax.plot(years, g_score, '^-', color='darkorange', linewidth=2.5,
        markersize=8, label='G (Governance)')

ax.axvline(x=2022, color='red', linestyle='--', linewidth=2,
           alpha=0.7, label='ChatGPT Launch')

ax.fill_between([2022, 2026], 45, 85, alpha=0.1, color='red')
ax.text(2024, 82, 'Post-ChatGPT\nAI Adoption Surge', ha='center', fontsize=10, style='italic')

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('ESG Pillar Score', fontsize=12)
ax.set_title('Predicted "Scissors" Pattern: ESG Pillar Divergence\nfor High AI-Adopting Firms', fontsize=13)
ax.legend(loc='lower left', fontsize=11)
ax.set_xlim(2017.5, 2026.5)
ax.set_ylim(50, 85)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig10_esg_scissors_pattern.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"    Saved: fig10_esg_scissors_pattern.png")

# Figure 11: Data Center Hub States Map (Conceptual Bar Chart)
fig, ax = plt.subplots(figsize=(12, 6))

hub_states = list(tech_hub_states.keys())
# Estimated data center capacity rankings (illustrative)
capacity_ranks = [100, 45, 35, 25, 20, 18, 15, 12, 10, 8]

colors = plt.cm.Reds(np.linspace(0.3, 0.9, len(hub_states)))
bars = ax.barh(hub_states[::-1], capacity_ranks[::-1], color=colors[::-1])

ax.set_xlabel('Relative Data Center Capacity (VA = 100)', fontsize=12)
ax.set_title('Major Data Center Hub States\n(Identification for Utility Electricity Analysis)', fontsize=13)

# Add annotations
for bar, state in zip(bars, hub_states[::-1]):
    width = bar.get_width()
    desc = tech_hub_states[state].split('(')[0].strip()
    ax.text(width + 2, bar.get_y() + bar.get_height()/2,
            desc, va='center', fontsize=9)

ax.set_xlim(0, 140)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig11_data_center_hubs.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"    Saved: fig11_data_center_hubs.png")

# =============================================================================
# SAVE RESULTS SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("SAVING RESULTS SUMMARY")
print("=" * 70)

# Save builder/user classification
classification = sp500[['ticker', 'company', 'GICS_sector', 'is_builder', 'is_user']].copy()
classification['firm_type'] = np.where(
    classification['is_builder'], 'Builder',
    np.where(classification['is_user'], 'User', 'Other')
)
classification.to_csv(OUTPUT_DIR / 'sp500_ai_classification.csv', index=False)
print(f"    Saved: sp500_ai_classification.csv")

# Save Big Tech emissions comparison
big_tech_data.to_csv(OUTPUT_DIR / 'big_tech_emissions_panel.csv', index=False)
print(f"    Saved: big_tech_emissions_panel.csv")

# Summary statistics
summary = {
    'Analysis': [
        'Builder firms in S&P 500',
        'User firms in S&P 500',
        'Builder firm-years in GHGRP',
        'User firm-years in GHGRP',
        'Tech hub states identified',
        'Big Tech emissions growth (avg 2020-2023)'
    ],
    'Value': [
        sp500['is_builder'].sum(),
        sp500['is_user'].sum(),
        ghgrp_classified['is_builder'].sum(),
        ghgrp_classified['is_user'].sum(),
        len(tech_hub_states),
        f"{emissions_growth['emissions_growth_pct'].mean():.1f}%"
    ]
}
summary_df = pd.DataFrame(summary)
summary_df.to_csv(OUTPUT_DIR / 'strategy_summary.csv', index=False)
print(f"    Saved: strategy_summary.csv")

# =============================================================================
# NEXT STEPS
# =============================================================================

print("\n" + "=" * 70)
print("NEXT STEPS FOR FULL IMPLEMENTATION")
print("=" * 70)

print("""
1. EIA FORM 861 DATA (Strategy 2):
   - Download: https://www.eia.gov/electricity/data/eia861/
   - Years needed: 2018-2024
   - Run utility-level DiD for tech hub vs. non-hub states

2. ESG SCORE DATA (Strategy 1):
   - Option A: S&P Global free tier (register at spglobal.com)
   - Option B: Refinitiv ESG (academic access)
   - Option C: Scrape available public ratings
   - Need E, S, G pillar scores separately

3. AI ADOPTION INTENSITY MEASURES:
   - SEC EDGAR 10-K scraper ready (run scripts/sec_edgar_scraper.py)
   - Extract: 'artificial intelligence', 'machine learning', 'generative AI'
   - Count mentions as AI adoption intensity proxy

4. EXPAND STOCK DATA (Strategy 3):
   - Currently have 8 tech firms
   - Need broader S&P 500 coverage for cross-sectional analysis
   - Calculate abnormal returns using Fama-French factors

5. INSTITUTIONAL OWNERSHIP (Strategy 3):
   - Download 13F filings from SEC EDGAR
   - Track ESG-focused institutional investor holdings
   - Test if ESG investors divest from high-emission AI adopters
""")

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
