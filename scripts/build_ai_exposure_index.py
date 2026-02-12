"""
Build AI Exposure Index from O*NET Data
========================================

Based on Felten, Raj, and Seamans (2021) methodology.

AI capabilities are matched to O*NET cognitive abilities:
- Language understanding: Oral/Written Comprehension
- Language generation: Oral/Written Expression
- Reasoning: Deductive, Inductive, Mathematical Reasoning
- Information processing: Information Ordering, Category Flexibility
- Pattern recognition: Perceptual Speed, Flexibility of Closure

Output: Occupation-level and industry-level AI exposure scores
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
AI_DIR = DATA_DIR / "ai_exposure"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis" / "output"

# =============================================================================
# AI-RELATED ABILITIES (based on Felten et al. and LLM capabilities)
# =============================================================================

# Abilities where AI (especially LLMs) has strong capability
# Higher exposure = more tasks AI can perform
AI_ABILITIES = {
    # Language abilities - HIGH AI exposure (LLMs excel here)
    '1.A.1.a.1': ('Oral Comprehension', 0.9),
    '1.A.1.a.2': ('Written Comprehension', 0.95),
    '1.A.1.a.3': ('Oral Expression', 0.85),
    '1.A.1.a.4': ('Written Expression', 0.95),

    # Reasoning abilities - HIGH AI exposure
    '1.A.1.b.4': ('Deductive Reasoning', 0.85),
    '1.A.1.b.5': ('Inductive Reasoning', 0.80),
    '1.A.1.c.1': ('Mathematical Reasoning', 0.90),
    '1.A.1.c.2': ('Number Facility', 0.95),

    # Information processing - MODERATE-HIGH AI exposure
    '1.A.1.b.6': ('Information Ordering', 0.85),
    '1.A.1.b.7': ('Category Flexibility', 0.75),
    '1.A.1.b.1': ('Fluency of Ideas', 0.70),
    '1.A.1.b.2': ('Originality', 0.50),  # AI less creative
    '1.A.1.b.3': ('Problem Sensitivity', 0.65),

    # Perceptual abilities - MODERATE AI exposure (computer vision)
    '1.A.2.a.2': ('Perceptual Speed', 0.80),
    '1.A.2.b.1': ('Flexibility of Closure', 0.60),
    '1.A.2.c.1': ('Spatial Orientation', 0.50),

    # Memory - MODERATE AI exposure
    '1.A.1.d.1': ('Memorization', 0.90),  # AI has perfect recall

    # Physical abilities - LOW AI exposure (require robotics)
    '1.A.2.a.1': ('Near Vision', 0.40),
    '1.A.3.a.1': ('Arm-Hand Steadiness', 0.20),
    '1.A.4.a.4': ('Stamina', 0.05),
}

# Work activities where AI can substitute
AI_WORK_ACTIVITIES = {
    # Information input - HIGH AI exposure
    '4.A.1.a.1': ('Getting Information', 0.85),
    '4.A.1.b.1': ('Identifying Objects, Actions, and Events', 0.70),

    # Mental processes - HIGH AI exposure
    '4.A.2.a.2': ('Processing Information', 0.90),
    '4.A.2.a.4': ('Analyzing Data or Information', 0.90),
    '4.A.2.b.1': ('Making Decisions and Solving Problems', 0.70),
    '4.A.2.b.2': ('Thinking Creatively', 0.55),
    '4.A.2.b.4': ('Developing Objectives and Strategies', 0.60),
    '4.A.2.b.5': ('Scheduling Work and Activities', 0.80),

    # Information output - HIGH AI exposure
    '4.A.3.a.1': ('Interpreting Information for Others', 0.80),
    '4.A.3.a.2': ('Communicating with Supervisors or Subordinates', 0.70),
    '4.A.3.a.3': ('Communicating with Outside Organizations', 0.70),
    '4.A.3.b.1': ('Documenting/Recording Information', 0.90),

    # Interacting with computers - VERY HIGH
    '4.A.3.b.6': ('Interacting With Computers', 0.95),

    # Physical activities - LOW AI exposure
    '4.A.3.a.4': ('Establishing and Maintaining Relationships', 0.40),
    '4.A.4.a.1': ('Performing General Physical Activities', 0.10),
    '4.A.4.b.4': ('Operating Vehicles or Equipment', 0.30),
}


def load_onet_data():
    """Load O*NET abilities and work activities data."""

    # Load abilities
    abilities = pd.read_csv(AI_DIR / 'onet_abilities.txt', sep='\t')
    abilities = abilities[abilities['Scale ID'] == 'IM']  # Importance scale
    abilities = abilities[['O*NET-SOC Code', 'Element ID', 'Element Name', 'Data Value']]
    abilities.columns = ['soc_code', 'element_id', 'element_name', 'importance']

    # Load work activities
    activities = pd.read_csv(AI_DIR / 'onet_work_activities.txt', sep='\t')
    activities = activities[activities['Scale ID'] == 'IM']  # Importance scale
    activities = activities[['O*NET-SOC Code', 'Element ID', 'Element Name', 'Data Value']]
    activities.columns = ['soc_code', 'element_id', 'element_name', 'importance']

    # Load occupation titles
    occupations = pd.read_csv(AI_DIR / 'onet_occupation_data.txt', sep='\t')
    occupations = occupations[['O*NET-SOC Code', 'Title']]
    occupations.columns = ['soc_code', 'occupation_title']

    return abilities, activities, occupations


def calculate_occupation_ai_exposure(abilities_df, activities_df):
    """Calculate AI exposure score for each occupation."""

    # Filter to AI-related abilities
    ai_ability_ids = list(AI_ABILITIES.keys())
    rel_abilities = abilities_df[abilities_df['element_id'].isin(ai_ability_ids)].copy()
    rel_abilities['ai_weight'] = rel_abilities['element_id'].map(
        {k: v[1] for k, v in AI_ABILITIES.items()}
    )

    # Filter to AI-related work activities
    ai_activity_ids = list(AI_WORK_ACTIVITIES.keys())
    rel_activities = activities_df[activities_df['element_id'].isin(ai_activity_ids)].copy()
    rel_activities['ai_weight'] = rel_activities['element_id'].map(
        {k: v[1] for k, v in AI_WORK_ACTIVITIES.items()}
    )

    # Calculate ability-based AI exposure per occupation
    # Formula: sum(importance * ai_weight) / sum(importance)
    ability_exposure = (rel_abilities
        .groupby('soc_code')
        .apply(lambda x: np.average(x['ai_weight'], weights=x['importance']))
        .reset_index(name='ability_ai_exposure'))

    # Calculate activity-based AI exposure per occupation
    activity_exposure = (rel_activities
        .groupby('soc_code')
        .apply(lambda x: np.average(x['ai_weight'], weights=x['importance']))
        .reset_index(name='activity_ai_exposure'))

    # Combine (equal weight to abilities and activities)
    exposure = ability_exposure.merge(activity_exposure, on='soc_code', how='outer')
    exposure['ai_exposure'] = exposure[['ability_ai_exposure', 'activity_ai_exposure']].mean(axis=1)

    # Normalize to 0-100 scale
    exposure['ai_exposure_normalized'] = (
        (exposure['ai_exposure'] - exposure['ai_exposure'].min()) /
        (exposure['ai_exposure'].max() - exposure['ai_exposure'].min()) * 100
    )

    return exposure


def map_soc_to_gics():
    """Create mapping from SOC occupation codes to GICS sectors."""

    # SOC major groups to GICS sector mapping
    # This is approximate - ideally would use BLS industry-occupation matrices
    soc_to_gics = {
        # Management occupations
        '11': 'Industrials',  # General management across sectors

        # Business and Financial
        '13': 'Financials',

        # Computer and Mathematical
        '15': 'Information Technology',

        # Architecture and Engineering
        '17': 'Industrials',

        # Life, Physical, Social Science
        '19': 'Health Care',

        # Community and Social Service
        '21': 'Health Care',

        # Legal
        '23': 'Financials',

        # Educational Instruction
        '25': 'Consumer Discretionary',

        # Arts, Design, Entertainment
        '27': 'Communication Services',

        # Healthcare Practitioners
        '29': 'Health Care',

        # Healthcare Support
        '31': 'Health Care',

        # Protective Service
        '33': 'Industrials',

        # Food Preparation
        '35': 'Consumer Discretionary',

        # Building and Grounds
        '37': 'Real Estate',

        # Personal Care
        '39': 'Consumer Discretionary',

        # Sales
        '41': 'Consumer Discretionary',

        # Office and Administrative
        '43': 'Industrials',

        # Farming, Fishing, Forestry
        '45': 'Consumer Staples',

        # Construction
        '47': 'Industrials',

        # Installation, Maintenance
        '49': 'Industrials',

        # Production
        '51': 'Materials',

        # Transportation
        '53': 'Industrials',

        # Military (not typically in S&P 500)
        '55': 'Industrials',
    }

    # Add manual sector exposure for sectors without SOC mapping
    # Based on typical workforce composition
    manual_sector_exposure = {
        'Energy': 45.0,      # Mix of engineers, analysts, field workers
        'Utilities': 42.0,   # Similar to energy - operations heavy
    }

    return soc_to_gics, manual_sector_exposure


def calculate_sector_ai_exposure(occ_exposure, occupations_df, soc_to_gics):
    """Calculate AI exposure by GICS sector."""

    # Merge occupation titles
    occ_exposure = occ_exposure.merge(occupations_df, on='soc_code', how='left')

    # Extract SOC major group (first 2 digits)
    occ_exposure['soc_major'] = occ_exposure['soc_code'].str[:2]

    # Map to GICS sector
    occ_exposure['gics_sector'] = occ_exposure['soc_major'].map(soc_to_gics)

    # Calculate sector-level exposure (simple average across occupations)
    # In practice, would weight by employment
    sector_exposure = (occ_exposure
        .groupby('gics_sector')
        .agg({
            'ai_exposure_normalized': ['mean', 'std', 'count'],
            'ability_ai_exposure': 'mean',
            'activity_ai_exposure': 'mean'
        })
        .round(2))

    sector_exposure.columns = ['ai_exposure', 'ai_exposure_std', 'n_occupations',
                               'ability_exposure', 'activity_exposure']
    sector_exposure = sector_exposure.reset_index()

    return occ_exposure, sector_exposure


def main():
    print("=" * 60)
    print("BUILDING AI EXPOSURE INDEX")
    print("=" * 60)

    # Load data
    print("\n1. Loading O*NET data...")
    abilities, activities, occupations = load_onet_data()
    print(f"   Abilities: {len(abilities)} records")
    print(f"   Work Activities: {len(activities)} records")
    print(f"   Occupations: {len(occupations)} unique")

    # Calculate occupation-level AI exposure
    print("\n2. Calculating occupation-level AI exposure...")
    occ_exposure = calculate_occupation_ai_exposure(abilities, activities)
    print(f"   Occupations with AI exposure scores: {len(occ_exposure)}")

    # Map to GICS sectors
    print("\n3. Mapping to GICS sectors...")
    soc_to_gics = map_soc_to_gics()
    occ_exposure, sector_exposure = calculate_sector_ai_exposure(
        occ_exposure, occupations, soc_to_gics
    )

    # Summary statistics
    print("\n" + "=" * 60)
    print("AI EXPOSURE BY GICS SECTOR")
    print("=" * 60)
    print(sector_exposure.sort_values('ai_exposure', ascending=False).to_string(index=False))

    # Top/bottom occupations
    print("\n" + "=" * 60)
    print("TOP 15 AI-EXPOSED OCCUPATIONS")
    print("=" * 60)
    top_occ = occ_exposure.nlargest(15, 'ai_exposure_normalized')[
        ['occupation_title', 'ai_exposure_normalized', 'gics_sector']
    ]
    for _, row in top_occ.iterrows():
        print(f"  {row['ai_exposure_normalized']:5.1f}  {row['occupation_title'][:50]:50} ({row['gics_sector']})")

    print("\n" + "=" * 60)
    print("BOTTOM 15 AI-EXPOSED OCCUPATIONS")
    print("=" * 60)
    bottom_occ = occ_exposure.nsmallest(15, 'ai_exposure_normalized')[
        ['occupation_title', 'ai_exposure_normalized', 'gics_sector']
    ]
    for _, row in bottom_occ.iterrows():
        print(f"  {row['ai_exposure_normalized']:5.1f}  {row['occupation_title'][:50]:50} ({row['gics_sector']})")

    # Save outputs
    print("\n" + "=" * 60)
    print("SAVING OUTPUTS")
    print("=" * 60)

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Occupation-level AI exposure
    occ_output = occ_exposure[['soc_code', 'occupation_title', 'ai_exposure_normalized',
                               'ability_ai_exposure', 'activity_ai_exposure', 'gics_sector']]
    occ_output.columns = ['soc_code', 'occupation', 'ai_exposure',
                          'ability_exposure', 'activity_exposure', 'gics_sector']
    occ_output.to_csv(OUTPUT_DIR / 'ai_exposure_by_occupation.csv', index=False)
    print(f"  Saved: ai_exposure_by_occupation.csv ({len(occ_output)} occupations)")

    # Sector-level AI exposure
    sector_exposure.to_csv(OUTPUT_DIR / 'ai_exposure_by_sector.csv', index=False)
    print(f"  Saved: ai_exposure_by_sector.csv ({len(sector_exposure)} sectors)")

    # Create firm-level AI exposure for S&P 500
    print("\n4. Matching AI exposure to S&P 500 firms...")
    sp500 = pd.read_csv(DATA_DIR / 'sp500_constituents.csv')

    # Merge sector AI exposure to S&P 500 firms
    firm_exposure = sp500.merge(
        sector_exposure[['gics_sector', 'ai_exposure']],
        left_on='GICS Sector', right_on='gics_sector', how='left'
    )
    firm_exposure = firm_exposure[['Symbol', 'Security', 'GICS Sector', 'GICS Sub-Industry', 'ai_exposure']]
    firm_exposure.columns = ['ticker', 'company', 'gics_sector', 'gics_subindustry', 'ai_exposure']

    # Create high/low AI exposure indicator
    median_exposure = firm_exposure['ai_exposure'].median()
    firm_exposure['high_ai_exposure'] = (firm_exposure['ai_exposure'] >= median_exposure).astype(int)

    firm_exposure.to_csv(OUTPUT_DIR / 'ai_exposure_sp500.csv', index=False)
    print(f"  Saved: ai_exposure_sp500.csv ({len(firm_exposure)} firms)")

    # Summary of firm-level exposure
    print("\n" + "=" * 60)
    print("S&P 500 AI EXPOSURE SUMMARY")
    print("=" * 60)
    print(f"\nMedian AI exposure: {median_exposure:.1f}")
    print(f"High AI exposure firms: {firm_exposure['high_ai_exposure'].sum()}")
    print(f"Low AI exposure firms: {(~firm_exposure['high_ai_exposure'].astype(bool)).sum()}")

    print("\nAI Exposure by Sector (S&P 500 firms):")
    sector_counts = firm_exposure.groupby('gics_sector').agg({
        'ai_exposure': 'first',
        'ticker': 'count',
        'high_ai_exposure': 'sum'
    }).sort_values('ai_exposure', ascending=False)
    sector_counts.columns = ['AI Exposure', 'N Firms', 'High Exposure']
    print(sector_counts.to_string())

    print("\n" + "=" * 60)
    print("AI EXPOSURE INDEX COMPLETE")
    print("=" * 60)

    return firm_exposure, sector_exposure


if __name__ == "__main__":
    firm_exposure, sector_exposure = main()
