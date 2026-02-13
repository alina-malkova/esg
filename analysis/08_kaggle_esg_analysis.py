#!/usr/bin/env python3
"""
Kaggle S&P 500 ESG Risk Ratings Analysis
Integrates Sustainalytics ESG risk scores with AI exposure analysis.

Data source: Kaggle "S&P 500 ESG Risk Ratings" by pritish509
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = BASE_DIR / 'analysis' / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300


def load_kaggle_esg():
    """Load Kaggle ESG dataset."""
    return pd.read_csv(DATA_DIR / 'kaggle_esg' / 'SP 500 ESG Risk Ratings.csv')


def load_ai_exposure():
    """Load AI exposure index by sector."""
    return pd.read_csv(BASE_DIR / 'analysis' / 'output' / 'ai_exposure_by_sector.csv')


def create_esg_by_sector_figure(df, ai_exposure):
    """Create ESG risk by sector with AI exposure overlay."""

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('S&P 500 ESG Risk by Sector vs AI Exposure', fontsize=14, fontweight='bold')

    # Calculate sector averages
    sector_esg = df.groupby('Sector').agg({
        'Total ESG Risk score': 'mean',
        'Environment Risk Score': 'mean',
        'Social Risk Score': 'mean',
        'Governance Risk Score': 'mean',
        'Symbol': 'count'
    }).rename(columns={'Symbol': 'count'}).dropna()

    # Map sector names to match AI exposure
    sector_map = {
        'Technology': 'Information Technology',
        'Financial Services': 'Financials',
        'Consumer Cyclical': 'Consumer Discretionary',
        'Consumer Defensive': 'Consumer Staples',
        'Communication Services': 'Communication Services',
        'Healthcare': 'Health Care',
        'Industrials': 'Industrials',
        'Real Estate': 'Real Estate',
        'Utilities': 'Utilities',
        'Basic Materials': 'Materials',
        'Energy': 'Energy'
    }

    sector_esg['sector_mapped'] = sector_esg.index.map(sector_map)

    # Merge with AI exposure
    if ai_exposure is not None:
        sector_esg = sector_esg.merge(
            ai_exposure[['gics_sector', 'ai_exposure']],
            left_on='sector_mapped',
            right_on='gics_sector',
            how='left'
        )
        sector_esg['ai_exposure_mean'] = sector_esg['ai_exposure']

    # Sort by total ESG risk
    sector_esg = sector_esg.sort_values('Total ESG Risk score')

    # Plot 1: ESG Risk by Sector
    ax1 = axes[0]
    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(sector_esg)))

    bars = ax1.barh(range(len(sector_esg)), sector_esg['Total ESG Risk score'], color=colors)
    ax1.set_yticks(range(len(sector_esg)))
    ax1.set_yticklabels(sector_esg.index)
    ax1.set_xlabel('Total ESG Risk Score (Higher = Worse)')
    ax1.set_title('(A) ESG Risk by Sector', fontweight='bold')
    ax1.axvline(x=sector_esg['Total ESG Risk score'].mean(), color='red',
                linestyle='--', label=f"Mean: {sector_esg['Total ESG Risk score'].mean():.1f}")
    ax1.legend()

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, sector_esg['Total ESG Risk score'])):
        ax1.text(val + 0.5, bar.get_y() + bar.get_height()/2, f'{val:.1f}',
                va='center', fontsize=9)

    # Plot 2: ESG vs AI Exposure scatter
    ax2 = axes[1]
    if 'ai_exposure_mean' in sector_esg.columns:
        scatter = ax2.scatter(sector_esg['ai_exposure_mean'],
                             sector_esg['Total ESG Risk score'],
                             s=sector_esg['count'] * 5,
                             c=sector_esg['Total ESG Risk score'],
                             cmap='RdYlGn_r', alpha=0.7, edgecolors='black')

        # Add sector labels
        for idx, row in sector_esg.iterrows():
            ax2.annotate(idx, (row['ai_exposure_mean'], row['Total ESG Risk score']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)

        ax2.set_xlabel('AI Exposure Score (O*NET-based)')
        ax2.set_ylabel('Total ESG Risk Score')
        ax2.set_title('(B) AI Exposure vs ESG Risk by Sector', fontweight='bold')

        # Add trend line
        z = np.polyfit(sector_esg['ai_exposure_mean'].dropna(),
                      sector_esg.loc[sector_esg['ai_exposure_mean'].notna(), 'Total ESG Risk score'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(sector_esg['ai_exposure_mean'].min(),
                            sector_esg['ai_exposure_mean'].max(), 100)
        ax2.plot(x_line, p(x_line), 'r--', alpha=0.5, label='Trend')

        # Calculate correlation
        corr = sector_esg[['ai_exposure_mean', 'Total ESG Risk score']].corr().iloc[0, 1]
        ax2.text(0.05, 0.95, f'Correlation: {corr:.2f}', transform=ax2.transAxes,
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig16_kaggle_esg_by_sector.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR / 'fig16_kaggle_esg_by_sector.png'}")


def create_esg_pillar_decomposition(df):
    """Create E, S, G pillar decomposition for AI builders vs users."""

    # Define AI builders
    ai_builders = ['MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'ORCL', 'IBM', 'CRM',
                   'NVDA', 'AMD', 'INTC', 'AVGO', 'QCOM', 'EQIX', 'DLR']

    df['is_ai_builder'] = df['Symbol'].isin(ai_builders)
    df['firm_type'] = df['is_ai_builder'].map({True: 'AI Infrastructure Builder',
                                                False: 'Other S&P 500'})

    # Filter to firms with ESG data
    df_esg = df[df['Total ESG Risk score'].notna()].copy()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('ESG Pillar Decomposition: AI Builders vs Other Firms',
                 fontsize=14, fontweight='bold')

    pillars = [
        ('Environment Risk Score', 'Environmental (E)', 'Greens'),
        ('Social Risk Score', 'Social (S)', 'Blues'),
        ('Governance Risk Score', 'Governance (G)', 'Purples')
    ]

    for ax, (col, title, cmap) in zip(axes, pillars):
        # Box plot
        builder_data = df_esg[df_esg['is_ai_builder']][col]
        other_data = df_esg[~df_esg['is_ai_builder']][col]

        bp = ax.boxplot([builder_data, other_data],
                       labels=['AI Builders\n(n={})'.format(len(builder_data)),
                              'Other Firms\n(n={})'.format(len(other_data))],
                       patch_artist=True)

        colors = ['#FF6B6B', '#4ECDC4']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Risk Score (Higher = Worse)')
        ax.set_title(title, fontweight='bold')

        # Add mean annotations
        means = [builder_data.mean(), other_data.mean()]
        for i, mean in enumerate(means):
            ax.annotate(f'μ={mean:.1f}', xy=(i+1, mean),
                       xytext=(10, 0), textcoords='offset points',
                       fontsize=10, color='red')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig17_esg_pillar_decomposition.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR / 'fig17_esg_pillar_decomposition.png'}")

    # Print summary statistics
    print("\n" + "=" * 70)
    print("ESG PILLAR COMPARISON: AI BUILDERS VS OTHER FIRMS")
    print("=" * 70)

    summary = df_esg.groupby('firm_type').agg({
        'Total ESG Risk score': ['mean', 'std', 'count'],
        'Environment Risk Score': 'mean',
        'Social Risk Score': 'mean',
        'Governance Risk Score': 'mean'
    }).round(2)

    print(summary)

    return df_esg


def create_big_tech_esg_detail(df):
    """Create detailed Big Tech ESG analysis."""

    big_tech = ['MSFT', 'GOOGL', 'GOOG', 'META', 'AMZN', 'AAPL', 'NVDA', 'TSLA']
    df_tech = df[df['Symbol'].isin(big_tech)].copy()
    df_tech = df_tech[df_tech['Total ESG Risk score'].notna()]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Sort by total ESG risk
    df_tech = df_tech.sort_values('Total ESG Risk score', ascending=True)

    x = np.arange(len(df_tech))
    width = 0.25

    bars1 = ax.bar(x - width, df_tech['Environment Risk Score'], width,
                   label='Environment', color='#2ECC71', alpha=0.8)
    bars2 = ax.bar(x, df_tech['Social Risk Score'], width,
                   label='Social', color='#3498DB', alpha=0.8)
    bars3 = ax.bar(x + width, df_tech['Governance Risk Score'], width,
                   label='Governance', color='#9B59B6', alpha=0.8)

    ax.set_xlabel('Company')
    ax.set_ylabel('ESG Risk Score (Higher = Worse)')
    ax.set_title('Big Tech ESG Risk Decomposition (Sustainalytics)', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df_tech['Symbol'])
    ax.legend()

    # Add total score labels
    for i, (idx, row) in enumerate(df_tech.iterrows()):
        ax.annotate(f"Total: {row['Total ESG Risk score']:.1f}\n({row['ESG Risk Level']})",
                   xy=(i, row['Total ESG Risk score']),
                   xytext=(0, 10), textcoords='offset points',
                   ha='center', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

    # Add horizontal line for S&P 500 average
    sp500_avg = df['Total ESG Risk score'].mean()
    ax.axhline(y=sp500_avg, color='red', linestyle='--',
               label=f'S&P 500 Avg: {sp500_avg:.1f}')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig18_big_tech_esg_detail.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {OUTPUT_DIR / 'fig18_big_tech_esg_detail.png'}")

    # Print table
    print("\n" + "=" * 70)
    print("BIG TECH ESG RISK SCORES (SUSTAINALYTICS)")
    print("=" * 70)
    print(df_tech[['Symbol', 'Name', 'Total ESG Risk score', 'Environment Risk Score',
                   'Social Risk Score', 'Governance Risk Score', 'ESG Risk Level']].to_string(index=False))


def main():
    """Main execution."""
    print("=" * 70)
    print("KAGGLE S&P 500 ESG ANALYSIS")
    print("=" * 70)

    # Load data
    df = load_kaggle_esg()
    print(f"Loaded {len(df)} companies, {df['Total ESG Risk score'].notna().sum()} with ESG scores")

    # Load AI exposure
    try:
        ai_exposure = load_ai_exposure()
        print(f"Loaded AI exposure for {len(ai_exposure)} sectors")
    except:
        ai_exposure = None
        print("AI exposure data not found")

    # Create figures
    print("\n1. Creating ESG by sector figure...")
    create_esg_by_sector_figure(df, ai_exposure)

    print("\n2. Creating ESG pillar decomposition...")
    create_esg_pillar_decomposition(df)

    print("\n3. Creating Big Tech ESG detail...")
    create_big_tech_esg_detail(df)

    # Save processed data
    output_file = OUTPUT_DIR / 'kaggle_esg_processed.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSaved processed data to: {output_file}")


if __name__ == '__main__':
    main()
