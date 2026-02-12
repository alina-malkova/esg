"""
PatentsView API Script for AI Patent Data
Fetches AI-related patents using the PatentsView API
"""

import requests
import pandas as pd
from pathlib import Path
import time
import json

BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data" / "patents"

# PatentsView API endpoint
API_URL = "https://api.patentsview.org/patents/query"

# AI-related CPC codes
AI_CPC_CODES = [
    "G06N",      # Machine learning, neural networks
    "G06F18",    # Pattern recognition
    "G06F40",    # Natural language processing
    "G10L",      # Speech recognition
    "G06V",      # Image recognition
    "G06Q",      # Business AI applications
]

def query_patents_by_cpc(cpc_code, per_page=1000, page=1):
    """Query patents by CPC code prefix"""

    query = {
        "_and": [
            {"_gte": {"patent_date": "2015-01-01"}},
            {"_begins": {"cpc_subgroup_id": cpc_code}}
        ]
    }

    fields = [
        "patent_id",
        "patent_title",
        "patent_date",
        "patent_year",
        "patent_abstract",
        "patent_num_claims",
        "assignee_organization",
        "assignee_type",
        "cpc_subgroup_id",
        "cpc_subgroup_title"
    ]

    params = {
        "q": json.dumps(query),
        "f": json.dumps(fields),
        "o": json.dumps({"page": page, "per_page": per_page}),
        "s": json.dumps([{"patent_date": "desc"}])
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API error for {cpc_code}: {e}")
        return None

def get_all_patents_for_cpc(cpc_code, max_patents=10000):
    """Get all patents for a CPC code with pagination"""
    all_patents = []
    page = 1
    per_page = 1000

    print(f"Fetching patents for CPC: {cpc_code}")

    while len(all_patents) < max_patents:
        result = query_patents_by_cpc(cpc_code, per_page=per_page, page=page)

        if not result or 'patents' not in result or not result['patents']:
            break

        patents = result['patents']
        all_patents.extend(patents)

        total_found = result.get('total_patent_count', 0)
        print(f"  Page {page}: Got {len(patents)} patents (total so far: {len(all_patents)}, API total: {total_found})")

        if len(patents) < per_page:
            break

        page += 1
        time.sleep(0.5)  # Rate limiting

    return all_patents

def flatten_patent_data(patents):
    """Flatten nested patent data for DataFrame"""
    flat_data = []

    for patent in patents:
        base = {
            'patent_id': patent.get('patent_id'),
            'patent_title': patent.get('patent_title'),
            'patent_date': patent.get('patent_date'),
            'patent_year': patent.get('patent_year'),
            'patent_abstract': patent.get('patent_abstract', '')[:500] if patent.get('patent_abstract') else '',
            'patent_num_claims': patent.get('patent_num_claims'),
        }

        # Get first assignee
        assignees = patent.get('assignees', [])
        if assignees:
            base['assignee_organization'] = assignees[0].get('assignee_organization')
            base['assignee_type'] = assignees[0].get('assignee_type')
        else:
            base['assignee_organization'] = None
            base['assignee_type'] = None

        # Get CPC codes
        cpcs = patent.get('cpcs', [])
        base['cpc_codes'] = '; '.join([c.get('cpc_subgroup_id', '') for c in cpcs[:5]])

        flat_data.append(base)

    return flat_data

def main():
    """Fetch AI patents from all relevant CPC codes"""
    print("="*60)
    print("PatentsView API - AI Patent Extraction")
    print("="*60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    all_patents = []

    for cpc_code in AI_CPC_CODES:
        patents = get_all_patents_for_cpc(cpc_code, max_patents=5000)
        if patents:
            # Add source CPC code
            for p in patents:
                p['source_cpc'] = cpc_code
            all_patents.extend(patents)
        time.sleep(1)

    if all_patents:
        # Flatten and deduplicate by patent_id
        flat_data = flatten_patent_data(all_patents)
        df = pd.DataFrame(flat_data)
        df = df.drop_duplicates(subset=['patent_id'])

        # Save
        output_file = DATA_DIR / "ai_patents.csv"
        df.to_csv(output_file, index=False)
        print(f"\nSaved: {output_file}")
        print(f"Total unique AI patents: {len(df)}")

        # Summary by year
        print("\n=== Patents by Year ===")
        print(df.groupby('patent_year').size().sort_index(ascending=False).head(10))

        # Top assignees
        print("\n=== Top Assignees ===")
        top_assignees = df['assignee_organization'].value_counts().head(20)
        print(top_assignees)

        return df

    return None

def quick_test():
    """Quick test with just G06N (ML/Neural Networks)"""
    print("Quick test: Fetching G06N patents...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    patents = get_all_patents_for_cpc("G06N", max_patents=2000)

    if patents:
        flat_data = flatten_patent_data(patents)
        df = pd.DataFrame(flat_data)
        df.to_csv(DATA_DIR / "ai_patents_g06n_sample.csv", index=False)
        print(f"Saved {len(df)} G06N patents")
        return df
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        quick_test()
    else:
        main()
