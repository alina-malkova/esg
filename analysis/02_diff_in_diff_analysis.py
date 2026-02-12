"""
Diff-in-Diff Analysis: AI Exposure and Emissions
=================================================

Research Question: Does AI adoption pressure (post-ChatGPT) differentially
affect emissions for firms in high vs. low AI-exposed industries?

Identification Strategy:
- Treatment: High AI exposure industries × Post-ChatGPT (Nov 2022)
- Outcome: Firm-level emissions changes
- Model: Emissions_it = β(HighExposure_i × Post_t) + FirmFE + YearFE + ε
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"

# =============================================================================
# 1. LOAD AND MERGE DATA
# =============================================================================
print("=" * 70)
print("DIFF-IN-DIFF ANALYSIS: AI EXPOSURE AND EMISSIONS")
print("=" * 70)

# Load emissions panel
print("\n1. Loading data...")
emissions = pd.read_csv(DATA_DIR / "epa_ghgrp/processed/ghgrp_company_year_sp500_all_years.csv")
print(f"   Emissions panel: {len(emissions)} company-year obs")

# Load S&P 500 with sectors
sp500 = pd.read_csv(DATA_DIR / "sp500_constituents.csv")

# Merge sector info
emissions = emissions.merge(
    sp500[['Symbol', 'Security', 'GICS Sector']],
    left_on='ticker', right_on='Symbol', how='left'
)

# Define AI exposure by sector (from our analysis + manual for Energy/Utilities)
SECTOR_AI_EXPOSURE = {
    'Information Technology': 81.5,
    'Financials': 81.2,
    'Health Care': 65.1,
    'Consumer Discretionary': 62.6,
    'Communication Services': 58.8,
    'Industrials': 50.3,
    'Energy': 45.0,           # Manual estimate
    'Utilities': 42.0,        # Manual estimate
    'Materials': 37.2,
    'Consumer Staples': 29.6,
    'Real Estate': 28.9,
}

emissions['ai_exposure'] = emissions['GICS Sector'].map(SECTOR_AI_EXPOSURE)

# Create treatment variables
emissions['post_chatgpt'] = (emissions['year'] >= 2023).astype(int)
median_exposure = emissions['ai_exposure'].median()
emissions['high_ai_exposure'] = (emissions['ai_exposure'] >= median_exposure).astype(int)
emissions['treatment'] = emissions['high_ai_exposure'] * emissions['post_chatgpt']

# Log emissions for regression
emissions['log_emissions'] = np.log(emissions['total_emissions'] + 1)

# Create time variables
emissions['years_from_shock'] = emissions['year'] - 2022

print(f"   Firms: {emissions['ticker'].nunique()}")
print(f"   Years: {emissions['year'].min()}-{emissions['year'].max()}")
print(f"   High AI exposure firms: {emissions[emissions['high_ai_exposure']==1]['ticker'].nunique()}")
print(f"   Low AI exposure firms: {emissions[emissions['high_ai_exposure']==0]['ticker'].nunique()}")

# =============================================================================
# 2. SUMMARY STATISTICS
# =============================================================================
print("\n" + "=" * 70)
print("2. SUMMARY STATISTICS")
print("=" * 70)

# Pre/post means by treatment group
summary = emissions.groupby(['high_ai_exposure', 'post_chatgpt']).agg({
    'total_emissions': ['mean', 'std', 'count'],
    'log_emissions': ['mean', 'std']
}).round(2)
summary.columns = ['emissions_mean', 'emissions_std', 'n_obs', 'log_emissions_mean', 'log_emissions_std']

print("\n--- Mean Emissions by Treatment Group (Million Metric Tons) ---")
for (high_exp, post), row in summary.iterrows():
    group = "High AI Exp" if high_exp else "Low AI Exp"
    period = "Post-ChatGPT" if post else "Pre-ChatGPT"
    print(f"  {group:12} × {period:14}: {row['emissions_mean']/1e6:8.2f}M  (n={int(row['n_obs'])})")

# Calculate raw DiD estimate
pre_high = emissions[(emissions['high_ai_exposure']==1) & (emissions['post_chatgpt']==0)]['log_emissions'].mean()
post_high = emissions[(emissions['high_ai_exposure']==1) & (emissions['post_chatgpt']==1)]['log_emissions'].mean()
pre_low = emissions[(emissions['high_ai_exposure']==0) & (emissions['post_chatgpt']==0)]['log_emissions'].mean()
post_low = emissions[(emissions['high_ai_exposure']==0) & (emissions['post_chatgpt']==1)]['log_emissions'].mean()

did_raw = (post_high - pre_high) - (post_low - pre_low)
print(f"\n--- Raw Diff-in-Diff Estimate (Log Emissions) ---")
print(f"  High AI exposure change: {post_high - pre_high:+.4f}")
print(f"  Low AI exposure change:  {post_low - pre_low:+.4f}")
print(f"  Diff-in-Diff estimate:   {did_raw:+.4f} ({(np.exp(did_raw)-1)*100:+.2f}%)")

# =============================================================================
# 3. REGRESSION ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("3. REGRESSION ANALYSIS")
print("=" * 70)

# Model 1: Basic DiD (no fixed effects)
print("\n--- Model 1: Basic Diff-in-Diff ---")
model1 = smf.ols('log_emissions ~ high_ai_exposure * post_chatgpt', data=emissions).fit()
print(f"  DiD coefficient (HighExp × Post): {model1.params['high_ai_exposure:post_chatgpt']:.4f}")
print(f"  Standard error: {model1.bse['high_ai_exposure:post_chatgpt']:.4f}")
print(f"  P-value: {model1.pvalues['high_ai_exposure:post_chatgpt']:.4f}")
print(f"  R-squared: {model1.rsquared:.4f}")

# Model 2: With firm fixed effects
print("\n--- Model 2: Firm Fixed Effects ---")
emissions['firm_fe'] = pd.Categorical(emissions['ticker'])
model2 = smf.ols('log_emissions ~ treatment + C(year) + C(firm_fe)', data=emissions).fit()
print(f"  Treatment coefficient: {model2.params['treatment']:.4f}")
print(f"  Standard error: {model2.bse['treatment']:.4f}")
print(f"  P-value: {model2.pvalues['treatment']:.4f}")
print(f"  R-squared: {model2.rsquared:.4f}")

# Model 3: Continuous AI exposure
print("\n--- Model 3: Continuous AI Exposure ---")
emissions['ai_exposure_std'] = (emissions['ai_exposure'] - emissions['ai_exposure'].mean()) / emissions['ai_exposure'].std()
emissions['ai_post_interaction'] = emissions['ai_exposure_std'] * emissions['post_chatgpt']

model3 = smf.ols('log_emissions ~ ai_post_interaction + C(year) + C(firm_fe)', data=emissions).fit()
print(f"  AI Exposure × Post coefficient: {model3.params['ai_post_interaction']:.4f}")
print(f"  Standard error: {model3.bse['ai_post_interaction']:.4f}")
print(f"  P-value: {model3.pvalues['ai_post_interaction']:.4f}")
print(f"  Interpretation: 1 SD increase in AI exposure → {model3.params['ai_post_interaction']*100:.2f}% emissions change post-ChatGPT")

# =============================================================================
# 4. EVENT STUDY / PARALLEL TRENDS
# =============================================================================
print("\n" + "=" * 70)
print("4. EVENT STUDY (PARALLEL TRENDS CHECK)")
print("=" * 70)

# Create year dummies interacted with high_ai_exposure
# Reference year: 2022 (just before ChatGPT)
emissions['year_fe'] = emissions['year'].astype(str)

# Event study: interact each year with treatment
event_study_years = [2018, 2019, 2020, 2021, 2023]  # 2022 is reference
for yr in event_study_years:
    emissions[f'high_x_{yr}'] = ((emissions['year'] == yr) & (emissions['high_ai_exposure'] == 1)).astype(int)

# Run event study regression
event_formula = 'log_emissions ~ ' + ' + '.join([f'high_x_{yr}' for yr in event_study_years]) + ' + C(year) + C(firm_fe)'
event_model = smf.ols(event_formula, data=emissions).fit()

print("\n--- Event Study Coefficients (ref: 2022) ---")
event_coefs = []
for yr in event_study_years:
    coef = event_model.params[f'high_x_{yr}']
    se = event_model.bse[f'high_x_{yr}']
    pval = event_model.pvalues[f'high_x_{yr}']
    sig = "***" if pval < 0.01 else "**" if pval < 0.05 else "*" if pval < 0.1 else ""
    print(f"  {yr}: {coef:+.4f} (SE: {se:.4f}) {sig}")
    event_coefs.append({'year': yr, 'coef': coef, 'se': se, 'pval': pval})

event_coefs_df = pd.DataFrame(event_coefs)
event_coefs_df.loc[len(event_coefs_df)] = {'year': 2022, 'coef': 0, 'se': 0, 'pval': 1}
event_coefs_df = event_coefs_df.sort_values('year')

# =============================================================================
# 5. HETEROGENEITY ANALYSIS
# =============================================================================
print("\n" + "=" * 70)
print("5. HETEROGENEITY BY SECTOR")
print("=" * 70)

# Run DiD by sector
sector_results = []
for sector in emissions['GICS Sector'].dropna().unique():
    sector_data = emissions[emissions['GICS Sector'] == sector]
    if len(sector_data) > 20:  # Need enough obs
        try:
            model = smf.ols('log_emissions ~ post_chatgpt + C(ticker)', data=sector_data).fit()
            sector_results.append({
                'sector': sector,
                'post_coef': model.params['post_chatgpt'],
                'se': model.bse['post_chatgpt'],
                'pval': model.pvalues['post_chatgpt'],
                'n_firms': sector_data['ticker'].nunique(),
                'ai_exposure': SECTOR_AI_EXPOSURE.get(sector, np.nan)
            })
        except:
            pass

sector_df = pd.DataFrame(sector_results).sort_values('ai_exposure', ascending=False)
print("\n--- Post-ChatGPT Emissions Change by Sector ---")
for _, row in sector_df.iterrows():
    sig = "***" if row['pval'] < 0.01 else "**" if row['pval'] < 0.05 else "*" if row['pval'] < 0.1 else ""
    pct_change = (np.exp(row['post_coef']) - 1) * 100
    print(f"  {row['sector']:25} (AI: {row['ai_exposure']:5.1f}): {pct_change:+6.2f}% {sig}")

# =============================================================================
# 6. VISUALIZATIONS
# =============================================================================
print("\n" + "=" * 70)
print("6. GENERATING FIGURES")
print("=" * 70)

# Figure 1: Parallel trends
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Panel A: Mean emissions by treatment group over time
ax1 = axes[0]
for treat, label, color in [(1, 'High AI Exposure', 'red'), (0, 'Low AI Exposure', 'blue')]:
    group_data = emissions[emissions['high_ai_exposure'] == treat].groupby('year')['log_emissions'].mean()
    ax1.plot(group_data.index, group_data.values, '-o', color=color, linewidth=2, markersize=5, label=label)
ax1.axvline(x=2022.92, color='gray', linestyle='--', alpha=0.7, label='ChatGPT Launch')
ax1.set_xlabel('Year')
ax1.set_ylabel('Log Emissions (Mean)')
ax1.set_title('A. Parallel Trends: High vs Low AI Exposure')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Panel B: Event study plot
ax2 = axes[1]
ax2.errorbar(event_coefs_df['year'], event_coefs_df['coef'],
             yerr=1.96*event_coefs_df['se'], fmt='o-', capsize=4, capthick=2,
             color='darkblue', markersize=8, linewidth=2)
ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
ax2.axvline(x=2022, color='red', linestyle='--', alpha=0.7, label='ChatGPT Launch')
ax2.set_xlabel('Year')
ax2.set_ylabel('Coefficient (High AI Exp × Year)')
ax2.set_title('B. Event Study: Treatment Effect by Year')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig5_parallel_trends.png', dpi=150, bbox_inches='tight')
print("  Saved: fig5_parallel_trends.png")

# Figure 2: Sector heterogeneity
fig, ax = plt.subplots(figsize=(10, 6))
sector_df_plot = sector_df.sort_values('post_coef')
colors = ['green' if x < 0 else 'red' for x in sector_df_plot['post_coef']]
pct_changes = (np.exp(sector_df_plot['post_coef']) - 1) * 100
ax.barh(sector_df_plot['sector'], pct_changes, color=colors, alpha=0.7)
ax.axvline(x=0, color='black', linewidth=0.8)
ax.set_xlabel('% Change in Emissions (Post-ChatGPT)')
ax.set_title('Emissions Change by Sector After ChatGPT (Firm FE)')

# Add AI exposure annotation
for i, (_, row) in enumerate(sector_df_plot.iterrows()):
    ax.annotate(f'AI: {row["ai_exposure"]:.0f}', xy=(0.5, i), fontsize=9, va='center')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'fig6_sector_heterogeneity.png', dpi=150, bbox_inches='tight')
print("  Saved: fig6_sector_heterogeneity.png")

plt.close('all')

# =============================================================================
# 7. EXPORT RESULTS
# =============================================================================
print("\n" + "=" * 70)
print("7. EXPORTING RESULTS")
print("=" * 70)

# Export regression results
results_summary = pd.DataFrame({
    'Model': ['Basic DiD', 'Firm FE', 'Continuous AI'],
    'Coefficient': [
        model1.params['high_ai_exposure:post_chatgpt'],
        model2.params['treatment'],
        model3.params['ai_post_interaction']
    ],
    'SE': [
        model1.bse['high_ai_exposure:post_chatgpt'],
        model2.bse['treatment'],
        model3.bse['ai_post_interaction']
    ],
    'P-value': [
        model1.pvalues['high_ai_exposure:post_chatgpt'],
        model2.pvalues['treatment'],
        model3.pvalues['ai_post_interaction']
    ],
    'R-squared': [model1.rsquared, model2.rsquared, model3.rsquared]
})
results_summary.to_csv(OUTPUT_DIR / 'did_regression_results.csv', index=False)
print("  Saved: did_regression_results.csv")

# Export event study coefficients
event_coefs_df.to_csv(OUTPUT_DIR / 'event_study_coefficients.csv', index=False)
print("  Saved: event_study_coefficients.csv")

# Export analysis dataset
analysis_cols = ['ticker', 'year', 'total_emissions', 'log_emissions', 'GICS Sector',
                 'ai_exposure', 'high_ai_exposure', 'post_chatgpt', 'treatment']
emissions[analysis_cols].to_csv(OUTPUT_DIR / 'did_analysis_data.csv', index=False)
print("  Saved: did_analysis_data.csv")

# =============================================================================
# 8. SUMMARY
# =============================================================================
print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)

print(f"""
KEY FINDINGS:

1. DIFF-IN-DIFF ESTIMATE (High AI Exposure × Post-ChatGPT):
   - Basic DiD: {model1.params['high_ai_exposure:post_chatgpt']:+.4f} (p={model1.pvalues['high_ai_exposure:post_chatgpt']:.3f})
   - With Firm FE: {model2.params['treatment']:+.4f} (p={model2.pvalues['treatment']:.3f})

2. INTERPRETATION:
   - The coefficient of {model2.params['treatment']:+.4f} implies high AI exposure firms
     changed emissions by {(np.exp(model2.params['treatment'])-1)*100:+.2f}% more than low exposure firms
     after ChatGPT launch.

3. PARALLEL TRENDS:
   - Pre-treatment coefficients (2018-2021): Check if close to zero
   - Post-treatment (2023): {event_coefs_df[event_coefs_df['year']==2023]['coef'].values[0]:+.4f}

4. HETEROGENEITY:
   - Largest emissions reductions: {sector_df.iloc[0]['sector']}
   - Largest emissions increases: {sector_df.iloc[-1]['sector']}

CAVEATS:
- Only 1 year of post-treatment data (2023)
- GHGRP captures direct emissions only (Scope 1), missing electricity (Scope 2)
- Tech firms with data center emissions may report via electricity providers
- Need additional controls: firm size, regional grid intensity, energy prices
""")

print("=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
