#!/usr/bin/env python3
"""
Multi-source ESG analysis combining:
1. Sustainalytics (Kaggle) - ESG Risk Ratings
2. Fortune Most Admired Companies
3. Newsweek Most Responsible Companies
4. MSCI ratings (manual)
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Output directory
output_dir = project_root / 'analysis' / 'output'
output_dir.mkdir(parents=True, exist_ok=True)

def load_all_esg_sources():
    """Load and merge all ESG data sources."""

    data = {}

    # 1. Kaggle Sustainalytics
    kaggle_path = project_root / 'data' / 'kaggle_esg' / 'SP 500 ESG Risk Ratings.csv'
    if kaggle_path.exists():
        data['sustainalytics'] = pd.read_csv(kaggle_path)
        print(f"Sustainalytics: {len(data['sustainalytics'])} firms")

    # 2. Fortune Most Admired
    fortune_path = project_root / 'data' / 'esg_scores' / 'fortune_most_admired.csv'
    if fortune_path.exists():
        data['fortune'] = pd.read_csv(fortune_path)
        print(f"Fortune Most Admired: {len(data['fortune'])} firms")

    # 3. Newsweek Most Responsible
    newsweek_path = project_root / 'data' / 'esg_scores' / 'newsweek_responsible.csv'
    if newsweek_path.exists():
        data['newsweek'] = pd.read_csv(newsweek_path)
        print(f"Newsweek Most Responsible: {len(data['newsweek'])} firms")

    # 4. Big Tech MSCI panel
    msci_path = project_root / 'data' / 'esg_scores' / 'big_tech_esg_manual.csv'
    if msci_path.exists():
        data['msci'] = pd.read_csv(msci_path)
        print(f"MSCI Big Tech Panel: {len(data['msci'])} observations")

    return data


def analyze_big_tech_across_sources(data):
    """Compare Big Tech rankings across different ESG sources."""

    print("\n" + "=" * 70)
    print("BIG TECH ESG RANKINGS ACROSS SOURCES")
    print("=" * 70)

    big_tech = {
        'Apple': {'ticker': 'AAPL', 'fortune': 1},
        'Microsoft': {'ticker': 'MSFT', 'fortune': 2},
        'Amazon': {'ticker': 'AMZN', 'fortune': 3},
        'NVIDIA': {'ticker': 'NVDA', 'fortune': 4},
        'Alphabet': {'ticker': 'GOOGL', 'fortune': 8},
        'Meta': {'ticker': 'META', 'fortune': None}
    }

    # Get Sustainalytics scores
    sust = data.get('sustainalytics')
    if sust is not None:
        for company, info in big_tech.items():
            ticker = info['ticker']
            row = sust[sust['Symbol'] == ticker]
            if not row.empty:
                info['sust_total'] = row['Total ESG Risk score'].values[0]
                info['sust_env'] = row['Environment Risk Score'].values[0]
                info['sust_social'] = row['Social Risk Score'].values[0]
                info['sust_gov'] = row['Governance Risk Score'].values[0]

    # Get Newsweek rankings
    newsweek = data.get('newsweek')
    if newsweek is not None:
        for company, info in big_tech.items():
            # Match by company name
            match = newsweek[newsweek['company'].str.contains(company.split()[0], case=False, na=False)]
            if not match.empty:
                info['newsweek_rank'] = match['rank'].values[0]
                info['newsweek_score'] = match['score'].values[0]

    # Print comparison table
    print("\n{:<12} {:>10} {:>10} {:>10} {:>10} {:>12} {:>10}".format(
        "Company", "Fortune", "Newsweek", "NW Score", "Sust Risk", "Sust Env", "Rating"
    ))
    print("-" * 80)

    # Get MSCI 2023 ratings
    msci_2023 = {
        'AAPL': 'AA', 'MSFT': 'AAA', 'GOOGL': 'BB',
        'AMZN': 'BB', 'META': 'CCC', 'NVDA': 'AA'
    }

    for company, info in big_tech.items():
        fortune_rank = info.get('fortune', '-')
        newsweek_rank = info.get('newsweek_rank', '-')
        newsweek_score = info.get('newsweek_score', '-')
        sust_risk = info.get('sust_total', '-')
        sust_env = info.get('sust_env', '-')
        msci = msci_2023.get(info['ticker'], '-')

        print("{:<12} {:>10} {:>10} {:>10} {:>10} {:>12} {:>10}".format(
            company,
            fortune_rank if fortune_rank else '-',
            newsweek_rank if newsweek_rank else '-',
            f"{newsweek_score:.1f}" if isinstance(newsweek_score, (int, float)) else '-',
            f"{sust_risk:.1f}" if isinstance(sust_risk, (int, float)) else '-',
            f"{sust_env:.1f}" if isinstance(sust_env, (int, float)) else '-',
            msci
        ))

    return big_tech


def create_esg_comparison_figure(data, big_tech):
    """Create visualization comparing ESG ratings across sources."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Big Tech Sustainalytics Risk Scores
    ax1 = axes[0, 0]
    companies = ['Apple', 'Microsoft', 'Alphabet', 'Amazon', 'Meta', 'NVIDIA']
    total_risk = [big_tech[c].get('sust_total', 0) for c in companies]
    env_risk = [big_tech[c].get('sust_env', 0) for c in companies]

    x = np.arange(len(companies))
    width = 0.35

    bars1 = ax1.bar(x - width/2, total_risk, width, label='Total ESG Risk', color='steelblue')
    bars2 = ax1.bar(x + width/2, env_risk, width, label='Environmental Risk', color='forestgreen')

    ax1.set_ylabel('Risk Score (Lower = Better)')
    ax1.set_title('Big Tech ESG Risk Scores (Sustainalytics)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(companies, rotation=45, ha='right')
    ax1.legend()
    ax1.axhline(y=20, color='orange', linestyle='--', alpha=0.5, label='Low/Medium threshold')
    ax1.axhline(y=30, color='red', linestyle='--', alpha=0.5, label='Medium/High threshold')

    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.1f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    # 2. Fortune vs Sustainalytics
    ax2 = axes[0, 1]
    fortune_ranks = []
    sust_scores = []
    labels = []

    for company, info in big_tech.items():
        if info.get('fortune') and info.get('sust_total'):
            fortune_ranks.append(info['fortune'])
            sust_scores.append(info['sust_total'])
            labels.append(company)

    ax2.scatter(fortune_ranks, sust_scores, s=150, c='coral', edgecolors='black')
    for i, label in enumerate(labels):
        ax2.annotate(label, (fortune_ranks[i], sust_scores[i]),
                    xytext=(5, 5), textcoords='offset points', fontsize=10)

    ax2.set_xlabel('Fortune Most Admired Rank (Lower = Better)')
    ax2.set_ylabel('Sustainalytics Risk Score (Lower = Better)')
    ax2.set_title('Fortune Admiration vs ESG Risk')
    ax2.invert_xaxis()
    ax2.axhline(y=20, color='orange', linestyle='--', alpha=0.5)
    ax2.axhline(y=30, color='red', linestyle='--', alpha=0.5)

    # 3. MSCI Rating Distribution
    ax3 = axes[1, 0]
    msci_ratings = ['CCC', 'B', 'BB', 'BBB', 'A', 'AA', 'AAA']
    msci_2023 = {'AAPL': 'AA', 'MSFT': 'AAA', 'GOOGL': 'BB', 'AMZN': 'BB', 'META': 'CCC', 'NVDA': 'AA'}

    rating_counts = {r: 0 for r in msci_ratings}
    for ticker, rating in msci_2023.items():
        if rating in rating_counts:
            rating_counts[rating] += 1

    colors = ['darkred', 'red', 'orange', 'gold', 'yellowgreen', 'limegreen', 'darkgreen']
    ax3.bar(msci_ratings, [rating_counts[r] for r in msci_ratings], color=colors)
    ax3.set_xlabel('MSCI ESG Rating')
    ax3.set_ylabel('Number of Big Tech Firms')
    ax3.set_title('Big Tech MSCI Ratings Distribution (2023)')

    # Add company labels to bars
    for rating in msci_ratings:
        companies_with_rating = [t for t, r in msci_2023.items() if r == rating]
        if companies_with_rating:
            idx = msci_ratings.index(rating)
            ax3.annotate(', '.join(companies_with_rating),
                        xy=(idx, rating_counts[rating] + 0.1),
                        ha='center', fontsize=8, rotation=45)

    # 4. Newsweek scores for tech companies in top 50
    ax4 = axes[1, 1]
    newsweek = data.get('newsweek')
    if newsweek is not None:
        # Filter for tech-related companies
        tech_keywords = ['NVIDIA', 'Microsoft', 'Intel', 'HP', 'Cisco', 'QUALCOMM',
                        'Broadcom', 'Autodesk', 'Dell', 'AMD', 'PayPal', 'Micron']

        tech_newsweek = newsweek[newsweek['company'].str.contains('|'.join(tech_keywords), case=False, na=False)]
        tech_newsweek = tech_newsweek.sort_values('rank')

        if not tech_newsweek.empty:
            bars = ax4.barh(range(len(tech_newsweek)), tech_newsweek['score'].astype(float), color='teal')
            ax4.set_yticks(range(len(tech_newsweek)))
            ax4.set_yticklabels([f"#{r}: {c}" for r, c in zip(tech_newsweek['rank'], tech_newsweek['company'])])
            ax4.set_xlabel('Responsibility Score')
            ax4.set_title('Tech Companies in Newsweek Most Responsible (2024)')
            ax4.invert_yaxis()

    plt.tight_layout()
    plt.savefig(output_dir / 'fig19_multi_source_esg_comparison.png', dpi=150, bbox_inches='tight')
    plt.savefig(output_dir / 'fig19_multi_source_esg_comparison.pdf', bbox_inches='tight')
    print(f"\nSaved figure to {output_dir / 'fig19_multi_source_esg_comparison.png'}")
    plt.close()


def analyze_esg_consistency():
    """Analyze consistency between different ESG rating systems."""

    print("\n" + "=" * 70)
    print("ESG RATING CONSISTENCY ANALYSIS")
    print("=" * 70)

    # Key insight: Different ESG sources give different rankings
    print("""
Key Findings:

1. FORTUNE MOST ADMIRED (Reputation-based):
   - Apple #1, Microsoft #2, Amazon #3, NVIDIA #4, Alphabet #8
   - Measures overall corporate reputation, not just ESG

2. SUSTAINALYTICS (Risk-based, lower = better):
   - NVIDIA: 13.6 (Low Risk) - Best of Big Tech
   - Microsoft: 15.1 (Low Risk)
   - Apple: 17.2 (Low Risk)
   - Alphabet: 24.2 (Medium Risk)
   - Amazon: 30.6 (High Risk)
   - Meta: 34.1 (High Risk) - Worst of Big Tech

3. NEWSWEEK MOST RESPONSIBLE (CSR-focused):
   - HP #3 (score: 82.01)
   - Cisco #4 (score: 87.46)
   - NVIDIA #25 (score: 84.8)
   - Microsoft #34 (score: 87.25)
   - Intel #44 (score: 76.07)
   - AMD #49 (score: 79.71)
   - Apple, Amazon, Alphabet, Meta NOT in top 49

4. MSCI ESG RATINGS (2023):
   - Microsoft: AAA (Leader)
   - Apple: AA
   - NVIDIA: AA
   - Alphabet: BB (downgraded from A)
   - Amazon: BB (downgraded from BBB)
   - Meta: CCC (Laggard, downgraded from B)

KEY INSIGHT: AI infrastructure builders (Meta, Amazon, Alphabet) show
ESG deterioration while chip suppliers (NVIDIA) maintain good ratings.
This supports the "builder vs. user" decomposition in the research.
""")


def main():
    """Run multi-source ESG analysis."""

    print("MULTI-SOURCE ESG ANALYSIS")
    print("=" * 70)

    # Load all data
    data = load_all_esg_sources()

    # Analyze Big Tech across sources
    big_tech = analyze_big_tech_across_sources(data)

    # Create comparison visualization
    create_esg_comparison_figure(data, big_tech)

    # Analyze consistency
    analyze_esg_consistency()

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
