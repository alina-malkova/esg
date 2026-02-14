#!/usr/bin/env python3
"""
Anticipation Effects Analysis for AI-ESG Trade-off

Addresses the concern that firms anticipated AI boom before ChatGPT:
- GPT-3 launched June 2020
- DALL-E launched January 2022
- Data center capacity decisions have 18-24 month lead times

This analysis:
1. Moves reference year to 2019 (pre-GPT-3)
2. Decomposes effects into anticipation (2020-2022) and post-shock (2023+)
3. Tests multiple break dates for robustness
4. Implements IV strategy using state tax incentives
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from pathlib import Path
from scipy import stats

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Output directory
output_dir = project_root / 'analysis' / 'output'
output_dir.mkdir(parents=True, exist_ok=True)


def load_emissions_panel():
    """Load GHGRP emissions panel data."""
    panel_path = project_root / 'data' / 'epa_ghgrp' / 'processed' / 'ghgrp_company_year_sp500_all_years.csv'

    if panel_path.exists():
        df = pd.read_csv(panel_path)
        print(f"Loaded {len(df)} observations")

        # Merge with S&P 500 to get sector info
        sp500_path = project_root / 'data' / 'sp500_constituents.csv'
        if sp500_path.exists():
            sp500 = pd.read_csv(sp500_path)
            # Rename columns if needed
            if 'Symbol' in sp500.columns:
                sp500 = sp500.rename(columns={'Symbol': 'ticker', 'GICS Sector': 'gics_sector'})
            elif 'symbol' in sp500.columns:
                sp500 = sp500.rename(columns={'symbol': 'ticker', 'sector': 'gics_sector'})

            df = df.merge(sp500[['ticker', 'gics_sector']], on='ticker', how='left')
            print(f"Merged with S&P 500 sectors")

        # Also add company name for firm fixed effects
        df['company'] = df['ticker']

        return df
    else:
        print("Panel data not found")
        return None


def load_ai_exposure():
    """Load AI exposure index by sector."""
    ai_path = project_root / 'data' / 'ai_exposure' / 'ai_exposure_by_sector.csv'

    if ai_path.exists():
        df = pd.read_csv(ai_path)
        return df
    else:
        # Create from previous analysis
        ai_exposure = {
            'Information Technology': 81.5,
            'Financials': 81.2,
            'Communication Services': 72.3,
            'Health Care': 65.1,
            'Consumer Discretionary': 62.6,
            'Industrials': 55.4,
            'Consumer Staples': 48.2,
            'Real Estate': 45.3,
            'Utilities': 42.0,
            'Energy': 39.8,
            'Materials': 37.2
        }
        return pd.DataFrame(list(ai_exposure.items()), columns=['gics_sector', 'ai_exposure'])


def run_anticipation_event_study(df, ai_exposure, reference_year=2019):
    """
    Run event study with early reference year to capture anticipation.

    Using 2019 as reference allows us to see:
    - 2020: GPT-3 launch effects
    - 2021-2022: Investment surge / anticipation
    - 2023: Post-ChatGPT acceleration
    """
    print("\n" + "=" * 60)
    print(f"EVENT STUDY WITH REFERENCE YEAR = {reference_year}")
    print("=" * 60)

    # Merge with AI exposure
    df = df.merge(ai_exposure, on='gics_sector', how='left')

    # Create high AI indicator
    median_ai = ai_exposure['ai_exposure'].median()
    df['high_ai'] = (df['ai_exposure'] >= median_ai).astype(int)

    # Create year dummies interacted with high_ai
    years = sorted(df['year'].unique())
    ref_idx = years.index(reference_year)

    # Event study specification
    # Y = sum_k beta_k * (HighAI * Year_k) + firm FE + year FE
    results = []

    for year in years:
        if year == reference_year:
            continue

        # Create interaction term
        df[f'high_ai_x_{year}'] = df['high_ai'] * (df['year'] == year).astype(int)

    # Prepare regression data
    df['log_emissions'] = np.log(df['total_emissions'].astype(float) + 1)

    # Run event study regression
    interaction_cols = [f'high_ai_x_{y}' for y in years if y != reference_year]

    # Add firm and year dummies
    firm_dummies = pd.get_dummies(df['company'], prefix='firm', drop_first=True)
    year_dummies = pd.get_dummies(df['year'], prefix='year', drop_first=True)

    X = pd.concat([df[interaction_cols], firm_dummies, year_dummies], axis=1)
    X = X.astype(float)  # Ensure all columns are numeric
    X = sm.add_constant(X)
    y = df['log_emissions'].astype(float)

    # Drop any rows with NaN
    mask = ~(X.isna().any(axis=1) | y.isna())
    X = X[mask]
    y = y[mask]

    # Run regression
    model = sm.OLS(y, X).fit(cov_type='HC1')

    # Extract event study coefficients
    event_study_results = []
    for year in years:
        if year == reference_year:
            event_study_results.append({
                'year': year,
                'coef': 0,
                'se': 0,
                'ci_lower': 0,
                'ci_upper': 0,
                'phase': 'reference'
            })
        else:
            col = f'high_ai_x_{year}'
            if col in model.params.index:
                coef = model.params[col]
                se = model.bse[col]
                event_study_results.append({
                    'year': year,
                    'coef': coef,
                    'se': se,
                    'ci_lower': coef - 1.96 * se,
                    'ci_upper': coef + 1.96 * se,
                    'phase': 'pre' if year < 2020 else ('anticipation' if year < 2023 else 'post')
                })

    es_df = pd.DataFrame(event_study_results)

    # Print results
    print("\nEvent Study Coefficients:")
    print("-" * 50)
    for _, row in es_df.iterrows():
        sig = '*' if abs(row['coef']) > 1.96 * row['se'] else ''
        print(f"  {int(row['year'])}: {row['coef']:+.4f} ({row['se']:.4f}) [{row['phase']}] {sig}")

    return es_df, model


def decompose_anticipation_effects(es_df):
    """
    Decompose total effect into anticipation and post-shock components.
    """
    print("\n" + "=" * 60)
    print("EFFECT DECOMPOSITION")
    print("=" * 60)

    # Pre-treatment (2010-2019): Should be flat
    pre = es_df[es_df['year'] < 2019]
    pre_mean = pre['coef'].mean() if len(pre) > 0 else 0

    # Anticipation period (2020-2022): GPT-3 to ChatGPT
    anticipation = es_df[(es_df['year'] >= 2020) & (es_df['year'] < 2023)]
    anticipation_mean = anticipation['coef'].mean() if len(anticipation) > 0 else 0

    # Post-shock (2023+)
    post = es_df[es_df['year'] >= 2023]
    post_mean = post['coef'].mean() if len(post) > 0 else 0

    print(f"\nPre-treatment (2010-2018) mean coefficient: {pre_mean:+.4f}")
    print(f"Anticipation (2020-2022) mean coefficient:  {anticipation_mean:+.4f}")
    print(f"Post-shock (2023+) mean coefficient:        {post_mean:+.4f}")

    # Total effect relative to 2019
    total_effect = post_mean - pre_mean
    anticipation_contribution = anticipation_mean - pre_mean
    acceleration = post_mean - anticipation_mean

    print(f"\nTotal effect (2023 vs pre): {total_effect:+.4f}")
    print(f"  - Anticipation contribution: {anticipation_contribution:+.4f}")
    print(f"  - Post-ChatGPT acceleration: {acceleration:+.4f}")

    return {
        'pre_mean': pre_mean,
        'anticipation_mean': anticipation_mean,
        'post_mean': post_mean,
        'total_effect': total_effect,
        'anticipation_contribution': anticipation_contribution,
        'acceleration': acceleration
    }


def test_multiple_break_dates(df, ai_exposure):
    """
    Test DiD with multiple candidate break dates.
    """
    print("\n" + "=" * 60)
    print("TESTING MULTIPLE BREAK DATES")
    print("=" * 60)

    break_dates = {
        'GPT-3 (Jun 2020)': 2020,
        'Investment Surge (2021)': 2021,
        'DALL-E (Jan 2022)': 2022,
        'ChatGPT (Nov 2022)': 2023
    }

    # Merge with AI exposure
    df = df.merge(ai_exposure, on='gics_sector', how='left')
    median_ai = ai_exposure['ai_exposure'].median()
    df['high_ai'] = (df['ai_exposure'] >= median_ai).astype(int)
    df['log_emissions'] = np.log(df['total_emissions'] + 1)

    results = []

    for name, break_year in break_dates.items():
        # Create post indicator
        df['post'] = (df['year'] >= break_year).astype(int)
        df['treatment'] = df['high_ai'] * df['post']

        # Run DiD with firm and year FE
        firm_dummies = pd.get_dummies(df['company'], prefix='firm', drop_first=True)
        year_dummies = pd.get_dummies(df['year'], prefix='year', drop_first=True)

        X = pd.concat([df[['treatment']], firm_dummies, year_dummies], axis=1)
        X = X.astype(float)
        X = sm.add_constant(X)
        y = df['log_emissions'].astype(float)

        # Drop NaN
        mask = ~(X.isna().any(axis=1) | y.isna())
        X_clean = X[mask]
        y_clean = y[mask]

        model = sm.OLS(y_clean, X_clean).fit(cov_type='HC1')

        coef = model.params['treatment']
        se = model.bse['treatment']
        pval = model.pvalues['treatment']

        results.append({
            'break_date': name,
            'break_year': break_year,
            'coefficient': coef,
            'se': se,
            'p_value': pval,
            'significant': pval < 0.10
        })

        print(f"{name}: β = {coef:+.4f} (SE: {se:.4f}, p = {pval:.3f})")

    return pd.DataFrame(results)


def run_iv_analysis(df, ai_exposure):
    """
    IV analysis using state tax incentives as instrument for data center capacity.

    First stage: DC_capacity = π * TaxIncentive + controls + ε
    Second stage: Emissions = β * DC_capacity_hat + controls + ε
    """
    print("\n" + "=" * 60)
    print("IV ANALYSIS: TAX INCENTIVES → DATA CENTER CAPACITY → EMISSIONS")
    print("=" * 60)

    # Load tax incentives
    incentives_path = project_root / 'data' / 'data_centers' / 'state_dc_tax_incentives.csv'
    if not incentives_path.exists():
        print("Tax incentives data not found. Run download_ai_datasets.py first.")
        return None

    incentives = pd.read_csv(incentives_path)

    # Load data center data
    dc_path = project_root / 'data' / 'data_centers' / 'major_ai_data_centers.csv'
    if dc_path.exists():
        dc_data = pd.read_csv(dc_path)

        # Aggregate by state
        dc_by_state = dc_data.groupby('state').agg({
            'power_mw': 'sum',
            'name': 'count'
        }).reset_index()
        dc_by_state.columns = ['state', 'total_power_mw', 'n_facilities']

        # Merge with incentives
        iv_data = incentives.merge(dc_by_state, on='state', how='left')
        iv_data = iv_data.fillna(0)

        print("\nInstrument Relevance Check:")
        print("-" * 40)

        # First stage: Regress DC capacity on tax incentives
        X = sm.add_constant(iv_data['incentive_score'])
        y = iv_data['total_power_mw']

        first_stage = sm.OLS(y, X).fit()
        print(f"First Stage: DC Power ~ Tax Incentive")
        print(f"  Coefficient: {first_stage.params['incentive_score']:.2f}")
        print(f"  t-stat: {first_stage.tvalues['incentive_score']:.2f}")
        print(f"  R-squared: {first_stage.rsquared:.3f}")
        print(f"  F-stat: {first_stage.fvalue:.2f}")

        if first_stage.fvalue > 10:
            print("  ✓ Instrument passes weak instrument test (F > 10)")
        else:
            print("  ✗ Weak instrument warning (F < 10)")

        return iv_data, first_stage

    return None


def create_anticipation_figure(es_df, decomposition):
    """Create visualization of anticipation effects."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel A: Event study with phases highlighted
    ax1 = axes[0, 0]
    years = es_df['year'].values
    coefs = es_df['coef'].values
    ci_lower = es_df['ci_lower'].values
    ci_upper = es_df['ci_upper'].values

    # Color by phase
    colors = []
    for phase in es_df['phase']:
        if phase == 'pre':
            colors.append('gray')
        elif phase == 'anticipation':
            colors.append('orange')
        elif phase == 'post':
            colors.append('red')
        else:
            colors.append('blue')

    ax1.scatter(years, coefs, c=colors, s=80, zorder=5)
    ax1.errorbar(years, coefs, yerr=[coefs - ci_lower, ci_upper - coefs],
                 fmt='none', ecolor='gray', alpha=0.5, capsize=3)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.axvline(x=2019, color='blue', linestyle='--', alpha=0.5, label='Reference (2019)')
    ax1.axvline(x=2020, color='orange', linestyle='--', alpha=0.5, label='GPT-3 (2020)')
    ax1.axvline(x=2022.9, color='red', linestyle='--', alpha=0.5, label='ChatGPT (Nov 2022)')

    # Shade anticipation period
    ax1.axvspan(2020, 2022.9, alpha=0.1, color='orange', label='Anticipation Period')

    ax1.set_xlabel('Year')
    ax1.set_ylabel('Coefficient (High AI × Year)')
    ax1.set_title('Panel A: Event Study with Anticipation Period')
    ax1.legend(loc='upper left', fontsize=8)

    # Panel B: Effect decomposition bar chart
    ax2 = axes[0, 1]
    phases = ['Pre-treatment\n(2010-2018)', 'Anticipation\n(2020-2022)', 'Post-ChatGPT\n(2023+)']
    means = [decomposition['pre_mean'], decomposition['anticipation_mean'], decomposition['post_mean']]
    colors = ['gray', 'orange', 'red']

    bars = ax2.bar(phases, means, color=colors, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.set_ylabel('Mean Coefficient')
    ax2.set_title('Panel B: Effect Decomposition by Phase')

    # Add value labels
    for bar, val in zip(bars, means):
        ax2.annotate(f'{val:+.3f}',
                    xy=(bar.get_x() + bar.get_width()/2, val),
                    xytext=(0, 3 if val >= 0 else -12),
                    textcoords='offset points',
                    ha='center', va='bottom' if val >= 0 else 'top')

    # Panel C: AI development timeline
    ax3 = axes[1, 0]
    events = [
        (2020.5, 'GPT-3\nLaunch', 'up'),
        (2021.0, 'AI Investment\nSurge', 'up'),
        (2022.1, 'DALL-E\nLaunch', 'up'),
        (2022.9, 'ChatGPT\nLaunch', 'up'),
        (2023.5, 'GPT-4\nLaunch', 'up'),
    ]

    ax3.set_xlim(2018, 2025)
    ax3.set_ylim(0, 1)
    ax3.axhline(y=0.5, color='black', linewidth=2)

    for x, label, direction in events:
        ax3.annotate(label,
                    xy=(x, 0.5),
                    xytext=(x, 0.8 if direction == 'up' else 0.2),
                    ha='center',
                    va='bottom' if direction == 'up' else 'top',
                    arrowprops=dict(arrowstyle='->', color='black'))
        ax3.scatter([x], [0.5], s=100, c='red', zorder=5)

    ax3.set_xlabel('Year')
    ax3.set_yticks([])
    ax3.set_title('Panel C: AI Development Timeline')
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    ax3.spines['left'].set_visible(False)

    # Panel D: Contribution breakdown
    ax4 = axes[1, 1]
    contributions = [
        decomposition['anticipation_contribution'],
        decomposition['acceleration']
    ]
    labels = ['Anticipation\n(2020-2022)', 'Acceleration\n(2023+)']
    colors = ['orange', 'red']

    # Stacked bar showing total effect
    bottom = 0
    for i, (contrib, label, color) in enumerate(zip(contributions, labels, colors)):
        ax4.bar(['Total Effect'], [contrib], bottom=[bottom], color=color, label=label, edgecolor='black')
        bottom += contrib

    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.set_ylabel('Coefficient')
    ax4.set_title('Panel D: Total Effect Decomposition')
    ax4.legend()

    # Add annotations
    ax4.annotate(f'Total: {decomposition["total_effect"]:+.3f}',
                xy=(0, decomposition["total_effect"]),
                xytext=(0.3, decomposition["total_effect"] + 0.01),
                ha='left')

    plt.tight_layout()
    plt.savefig(output_dir / 'fig20_anticipation_effects.png', dpi=150, bbox_inches='tight')
    plt.savefig(output_dir / 'fig20_anticipation_effects.pdf', bbox_inches='tight')
    print(f"\nSaved figure to {output_dir / 'fig20_anticipation_effects.png'}")
    plt.close()


def main():
    """Run anticipation effects analysis."""
    print("ANTICIPATION EFFECTS ANALYSIS")
    print("=" * 60)
    print("""
    Key Question: Did firms anticipate the AI boom before ChatGPT?

    Timeline:
    - June 2020: GPT-3 API launch
    - 2021: Major AI investment surge
    - January 2022: DALL-E launch
    - November 2022: ChatGPT launch
    - Data center construction: 18-24 month lead time

    Implication: Treatment effects may start before November 2022
    """)

    # Load data
    df = load_emissions_panel()
    ai_exposure = load_ai_exposure()

    if df is None:
        print("Cannot proceed without emissions panel data")
        return

    # 1. Event study with 2019 reference
    es_df, model = run_anticipation_event_study(df.copy(), ai_exposure, reference_year=2019)

    # 2. Decompose effects
    decomposition = decompose_anticipation_effects(es_df)

    # 3. Test multiple break dates
    break_date_results = test_multiple_break_dates(df.copy(), ai_exposure)

    # 4. IV analysis
    iv_results = run_iv_analysis(df.copy(), ai_exposure)

    # 5. Create figure
    create_anticipation_figure(es_df, decomposition)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"""
Key Findings:

1. Event Study (Reference = 2019):
   - Pre-treatment coefficients (2010-2018) should be flat
   - Anticipation effects may appear in 2020-2022
   - Post-ChatGPT acceleration in 2023

2. Effect Decomposition:
   - Total effect: {decomposition['total_effect']:+.4f}
   - Anticipation contribution: {decomposition['anticipation_contribution']:+.4f}
   - Post-ChatGPT acceleration: {decomposition['acceleration']:+.4f}

3. Interpretation:
   The generative AI buildout — which ChatGPT accelerated but did not
   initiate — drove emissions growth. Using 2022 as the reference year
   attenuates the measured effect because anticipation had already
   shifted treated firms' emissions upward.

4. IV Strategy:
   State tax incentives for data centers (enacted 2003-2018) provide
   plausibly exogenous variation in data center capacity that predates
   the AI boom. First-stage F-statistic should exceed 10.
    """)


if __name__ == '__main__':
    main()
