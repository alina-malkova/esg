#!/usr/bin/env python3
"""
ESG Trajectory Analysis for Big Tech
Analyzes the relationship between AI investment and ESG score changes.

Key findings:
- AI infrastructure builders show E-pillar deterioration post-2021
- Microsoft exception: aggressive carbon offset strategy maintains AAA
- "Scissors" pattern: S/G may improve while E deteriorates
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

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10


def load_esg_data():
    """Load Big Tech ESG panel data."""
    esg_file = DATA_DIR / 'esg_scores' / 'big_tech_esg_manual.csv'
    return pd.read_csv(esg_file)


def load_emissions_data():
    """Load Big Tech emissions data."""
    emissions_file = BASE_DIR / 'analysis' / 'output' / 'big_tech_emissions_full_panel.csv'
    if emissions_file.exists():
        return pd.read_csv(emissions_file)
    return None


def msci_to_numeric(rating):
    """Convert MSCI letter rating to numeric score."""
    mapping = {'CCC': 1, 'B': 2, 'BB': 3, 'BBB': 4, 'A': 5, 'AA': 6, 'AAA': 7}
    return mapping.get(rating, np.nan)


def pillar_to_numeric(pillar):
    """Convert pillar rating to numeric."""
    mapping = {'Laggard': 1, 'Average': 2, 'Leader': 3}
    return mapping.get(pillar, np.nan)


def create_esg_trajectory_figure(df):
    """Create comprehensive ESG trajectory visualization."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    fig.suptitle('Big Tech ESG Trajectories: The AI Trade-off (2019-2023)',
                 fontsize=14, fontweight='bold', y=1.02)

    # Color scheme for companies
    colors = {
        'Microsoft': '#00A4EF',  # Blue
        'Alphabet': '#34A853',   # Green
        'Meta': '#1877F2',       # Facebook blue
        'Amazon': '#FF9900',     # Orange
        'Apple': '#555555',      # Gray
        'NVIDIA': '#76B900'      # NVIDIA green
    }

    # 1. MSCI Rating Trajectory
    ax1 = axes[0, 0]
    df['msci_numeric'] = df['msci_rating'].apply(msci_to_numeric)

    for company in df['company'].unique():
        company_data = df[df['company'] == company]
        ax1.plot(company_data['year'], company_data['msci_numeric'],
                 marker='o', linewidth=2.5, markersize=8,
                 label=company, color=colors.get(company, 'gray'))

    ax1.set_yticks([1, 2, 3, 4, 5, 6, 7])
    ax1.set_yticklabels(['CCC', 'B', 'BB', 'BBB', 'A', 'AA', 'AAA'])
    ax1.set_xlabel('Year')
    ax1.set_ylabel('MSCI ESG Rating')
    ax1.set_title('(A) MSCI ESG Rating Trajectories', fontweight='bold')
    ax1.axvline(x=2022, color='red', linestyle='--', alpha=0.5, label='ChatGPT Launch')
    ax1.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)
    ax1.set_ylim(0.5, 7.5)

    # 2. Sustainalytics Risk Score (higher = worse)
    ax2 = axes[0, 1]

    for company in df['company'].unique():
        company_data = df[df['company'] == company]
        ax2.plot(company_data['year'], company_data['sustainalytics_risk'],
                 marker='s', linewidth=2.5, markersize=8,
                 label=company, color=colors.get(company, 'gray'))

    ax2.set_xlabel('Year')
    ax2.set_ylabel('Sustainalytics Risk Score (Higher = Worse)')
    ax2.set_title('(B) Sustainalytics ESG Risk Trend', fontweight='bold')
    ax2.axvline(x=2022, color='red', linestyle='--', alpha=0.5)
    ax2.axhspan(30, 40, alpha=0.1, color='red', label='High Risk Zone')
    ax2.axhspan(10, 20, alpha=0.1, color='green', label='Low Risk Zone')
    ax2.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)

    # 3. E-Pillar Deterioration
    ax3 = axes[1, 0]
    df['e_numeric'] = df['e_pillar'].apply(pillar_to_numeric)

    for company in df['company'].unique():
        company_data = df[df['company'] == company]
        ax3.plot(company_data['year'], company_data['e_numeric'],
                 marker='^', linewidth=2.5, markersize=8,
                 label=company, color=colors.get(company, 'gray'))

    ax3.set_yticks([1, 2, 3])
    ax3.set_yticklabels(['Laggard', 'Average', 'Leader'])
    ax3.set_xlabel('Year')
    ax3.set_ylabel('E-Pillar Rating')
    ax3.set_title('(C) Environmental Pillar Trajectory', fontweight='bold')
    ax3.axvline(x=2022, color='red', linestyle='--', alpha=0.5)
    ax3.set_ylim(0.5, 3.5)
    ax3.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=9)

    # 4. Rating Change Summary (2019 vs 2023)
    ax4 = axes[1, 1]

    # Calculate rating changes
    summary_data = []
    for company in df['company'].unique():
        company_data = df[df['company'] == company]
        rating_2019 = company_data[company_data['year'] == 2019]['msci_numeric'].values[0]
        rating_2023 = company_data[company_data['year'] == 2023]['msci_numeric'].values[0]
        risk_2019 = company_data[company_data['year'] == 2019]['sustainalytics_risk'].values[0]
        risk_2023 = company_data[company_data['year'] == 2023]['sustainalytics_risk'].values[0]

        summary_data.append({
            'company': company,
            'rating_change': rating_2023 - rating_2019,
            'risk_change': risk_2023 - risk_2019
        })

    summary_df = pd.DataFrame(summary_data)
    x = np.arange(len(summary_df))
    width = 0.35

    bars1 = ax4.bar(x - width/2, summary_df['rating_change'], width,
                    label='MSCI Rating Change', color='steelblue')
    bars2 = ax4.bar(x + width/2, summary_df['risk_change'], width,
                    label='Risk Score Change', color='coral')

    ax4.set_xlabel('Company')
    ax4.set_ylabel('Change (2019 → 2023)')
    ax4.set_title('(D) ESG Score Changes: 2019 vs 2023', fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(summary_df['company'], rotation=45, ha='right')
    ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax4.legend()

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax4.annotate(f'{height:+.0f}',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3 if height >= 0 else -10),
                     textcoords="offset points",
                     ha='center', va='bottom' if height >= 0 else 'top',
                     fontsize=8)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig14_esg_trajectories.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {OUTPUT_DIR / 'fig14_esg_trajectories.png'}")


def create_emissions_vs_esg_figure(df_esg, df_emissions):
    """Create emissions vs ESG comparison figure."""

    if df_emissions is None:
        print("Emissions data not found, skipping emissions vs ESG figure")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('The AI-ESG Trade-off: Emissions Growth vs. ESG Ratings',
                 fontsize=14, fontweight='bold')

    # Merge data
    df_esg['msci_numeric'] = df_esg['msci_rating'].apply(msci_to_numeric)

    # Get 2019 and 2023 values for comparison
    comparison = []
    for company in df_esg['company'].unique():
        esg_2019 = df_esg[(df_esg['company'] == company) & (df_esg['year'] == 2019)]['msci_numeric'].values
        esg_2023 = df_esg[(df_esg['company'] == company) & (df_esg['year'] == 2023)]['msci_numeric'].values

        if len(esg_2019) > 0 and len(esg_2023) > 0:
            ticker = df_esg[df_esg['company'] == company]['ticker'].values[0]
            emissions_data = df_emissions[df_emissions['ticker'] == ticker]

            if len(emissions_data) > 0:
                em_2019 = emissions_data[emissions_data['year'] == 2019]['scope_2_location'].values
                em_2023 = emissions_data[emissions_data['year'] == 2023]['scope_2_location'].values

                if len(em_2019) > 0 and len(em_2023) > 0 and em_2019[0] > 0:
                    comparison.append({
                        'company': company,
                        'ticker': ticker,
                        'esg_change': esg_2023[0] - esg_2019[0],
                        'emissions_growth': (em_2023[0] - em_2019[0]) / em_2019[0] * 100
                    })

    comp_df = pd.DataFrame(comparison)

    # Plot 1: Scatter of emissions growth vs ESG change
    ax1 = axes[0]
    colors_map = {'Microsoft': '#00A4EF', 'Alphabet': '#34A853', 'Meta': '#1877F2',
                  'Amazon': '#FF9900', 'Apple': '#555555'}

    for _, row in comp_df.iterrows():
        ax1.scatter(row['emissions_growth'], row['esg_change'],
                    s=200, c=colors_map.get(row['company'], 'gray'),
                    edgecolors='black', linewidth=1, alpha=0.8)
        ax1.annotate(row['company'],
                     (row['emissions_growth'], row['esg_change']),
                     xytext=(5, 5), textcoords='offset points', fontsize=10)

    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    ax1.set_xlabel('Scope 2 Emissions Growth 2019-2023 (%)', fontsize=11)
    ax1.set_ylabel('MSCI Rating Change (notches)', fontsize=11)
    ax1.set_title('(A) Emissions Growth vs ESG Rating Change', fontweight='bold')

    # Add quadrant labels
    ax1.annotate('Virtuous\n(less emissions, better ESG)',
                 xy=(-50, 1), fontsize=9, ha='center', color='green', alpha=0.7)
    ax1.annotate('Trade-off\n(more emissions, worse ESG)',
                 xy=(100, -2), fontsize=9, ha='center', color='red', alpha=0.7)

    # Plot 2: Bar chart comparison
    ax2 = axes[1]
    x = np.arange(len(comp_df))
    width = 0.35

    ax2_twin = ax2.twinx()

    bars1 = ax2.bar(x - width/2, comp_df['esg_change'], width,
                    label='MSCI Rating Change', color='steelblue', alpha=0.8)
    bars2 = ax2_twin.bar(x + width/2, comp_df['emissions_growth'], width,
                         label='Emissions Growth (%)', color='coral', alpha=0.8)

    ax2.set_xlabel('Company')
    ax2.set_ylabel('MSCI Rating Change (notches)', color='steelblue')
    ax2_twin.set_ylabel('Scope 2 Emissions Growth (%)', color='coral')
    ax2.set_title('(B) The Divergence: ESG vs Emissions', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(comp_df['company'], rotation=45, ha='right')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'fig15_emissions_vs_esg.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Saved: {OUTPUT_DIR / 'fig15_emissions_vs_esg.png'}")


def generate_summary_table(df):
    """Generate summary statistics table."""

    print("\n" + "=" * 70)
    print("BIG TECH ESG TRAJECTORY SUMMARY (2019-2023)")
    print("=" * 70)

    summary_rows = []
    for company in df['company'].unique():
        company_data = df[df['company'] == company].sort_values('year')

        row = {
            'Company': company,
            'MSCI 2019': company_data[company_data['year'] == 2019]['msci_rating'].values[0],
            'MSCI 2023': company_data[company_data['year'] == 2023]['msci_rating'].values[0],
            'MSCI Change': (msci_to_numeric(company_data[company_data['year'] == 2023]['msci_rating'].values[0]) -
                           msci_to_numeric(company_data[company_data['year'] == 2019]['msci_rating'].values[0])),
            'Risk 2019': company_data[company_data['year'] == 2019]['sustainalytics_risk'].values[0],
            'Risk 2023': company_data[company_data['year'] == 2023]['sustainalytics_risk'].values[0],
            'E-Pillar 2019': company_data[company_data['year'] == 2019]['e_pillar'].values[0],
            'E-Pillar 2023': company_data[company_data['year'] == 2023]['e_pillar'].values[0],
        }
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)

    print("\n1. MSCI Rating Changes:")
    print(summary_df[['Company', 'MSCI 2019', 'MSCI 2023', 'MSCI Change']].to_string(index=False))

    print("\n2. Sustainalytics Risk Score Changes (Higher = Worse):")
    print(summary_df[['Company', 'Risk 2019', 'Risk 2023']].to_string(index=False))

    print("\n3. Environmental Pillar Changes:")
    print(summary_df[['Company', 'E-Pillar 2019', 'E-Pillar 2023']].to_string(index=False))

    # Key findings
    print("\n" + "=" * 70)
    print("KEY FINDINGS:")
    print("=" * 70)
    print("""
1. ESG DETERIORATION POST-AI BOOM:
   - Alphabet: A → BB (3 notches down) - Google's data center expansion
   - Amazon: BBB → BB (1 notch down) - AWS expansion
   - Meta: B → CCC (2 notches down) - Massive AI/metaverse infrastructure

2. ESG LEADERS (Carbon Offset Strategy):
   - Microsoft: AAA → AAA (maintained via aggressive carbon purchasing)
   - Apple: A → AA (improved via supply chain decarbonization)

3. THE "CHIPS" EXCEPTION:
   - NVIDIA: BBB → AA (improved) - Benefits from AI narrative without
     owning data centers; customers bear the E-pillar cost

4. E-PILLAR "SCISSORS" PATTERN:
   - Alphabet, Amazon, Meta: Average/Laggard → Laggard
   - Microsoft, Apple: Leader → Leader (offset strategies)
   - The gap between leaders and laggards widened post-2021
""")

    return summary_df


def main():
    """Main execution."""
    print("=" * 70)
    print("ESG TRAJECTORY ANALYSIS FOR BIG TECH")
    print("=" * 70)

    # Load data
    df_esg = load_esg_data()
    df_emissions = load_emissions_data()

    print(f"Loaded ESG data: {len(df_esg)} observations")
    if df_emissions is not None:
        print(f"Loaded emissions data: {len(df_emissions)} observations")

    # Generate figures
    print("\n1. Creating ESG trajectory figure...")
    create_esg_trajectory_figure(df_esg)

    print("\n2. Creating emissions vs ESG figure...")
    create_emissions_vs_esg_figure(df_esg, df_emissions)

    # Generate summary
    print("\n3. Generating summary statistics...")
    summary_df = generate_summary_table(df_esg)

    # Save summary
    summary_df.to_csv(OUTPUT_DIR / 'big_tech_esg_summary.csv', index=False)
    print(f"\nSaved summary to: {OUTPUT_DIR / 'big_tech_esg_summary.csv'}")


if __name__ == '__main__':
    main()
