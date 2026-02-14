#!/usr/bin/env python3
"""
Scrape ESG data from multiple free sources:
1. Just Capital API
2. Corporate Knights Global 100
3. Fortune Most Admired Companies
"""

import os
import sys
import re
import json
import pandas as pd
import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Output directory
output_dir = project_root / 'data' / 'esg_scores'
output_dir.mkdir(parents=True, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def scrape_just_capital_api():
    """Fetch Just Capital API data."""
    print("\n" + "=" * 60)
    print("JUST CAPITAL API")
    print("=" * 60)

    url = "https://api.justcapital.com/rankings"

    try:
        resp = requests.get(url, headers={'Accept': 'application/json', **HEADERS}, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('content-type', 'unknown')}")

        if resp.status_code == 200:
            # Check if it's JSON
            try:
                data = resp.json()
                print(f"Got JSON with {len(data) if isinstance(data, list) else 'dict'} items")

                if isinstance(data, list) and len(data) > 0:
                    df = pd.DataFrame(data)
                    df.to_csv(output_dir / 'just_capital_api.csv', index=False)
                    print(f"Saved to data/esg_scores/just_capital_api.csv")
                    return df
                elif isinstance(data, dict):
                    # Check for nested data
                    for key in ['rankings', 'companies', 'data', 'results']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list):
                                df = pd.DataFrame(items)
                                df.to_csv(output_dir / 'just_capital_api.csv', index=False)
                                print(f"Saved to data/esg_scores/just_capital_api.csv")
                                return df
            except json.JSONDecodeError:
                print("Not JSON, checking HTML content...")
                # Save HTML for analysis
                with open(output_dir / 'just_capital_api_response.html', 'w') as f:
                    f.write(resp.text)
                print(f"Response saved ({len(resp.text)} chars)")

    except Exception as e:
        print(f"Error: {e}")

    return None


def scrape_corporate_knights():
    """Scrape Corporate Knights Global 100 rankings."""
    print("\n" + "=" * 60)
    print("CORPORATE KNIGHTS GLOBAL 100")
    print("=" * 60)

    url = "https://www.corporateknights.com/rankings/global-100-rankings/"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            rankings = []

            # Try to find ranking tables or lists
            # Method 1: Look for table
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")

            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        text = [c.get_text(strip=True) for c in cells]
                        # Check if first cell is a rank number
                        if text[0].isdigit():
                            rankings.append({
                                'rank': int(text[0]),
                                'company': text[1],
                                'country': text[2] if len(text) > 2 else '',
                                'score': text[-1] if len(text) > 3 else ''
                            })

            # Method 2: Look for ranking divs/articles
            if not rankings:
                articles = soup.find_all(['article', 'div'], class_=re.compile(r'rank|company|item'))
                print(f"Found {len(articles)} article/div elements")

                for article in articles[:200]:
                    text = article.get_text(strip=True)
                    # Try to parse rank and company
                    match = re.search(r'^(\d+)[\.\s]+([A-Za-z][A-Za-z0-9\s\.\-&]+)', text)
                    if match:
                        rankings.append({
                            'rank': int(match.group(1)),
                            'company': match.group(2).strip(),
                            'source': 'Corporate Knights Global 100'
                        })

            # Method 3: Look for JSON data in script tags
            if not rankings:
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and ('ranking' in script.string.lower() or 'company' in script.string.lower()):
                        # Try to extract JSON
                        json_match = re.search(r'\[{[^\]]+}\]', script.string)
                        if json_match:
                            try:
                                data = json.loads(json_match.group())
                                if isinstance(data, list):
                                    rankings = data
                                    print(f"Found JSON data with {len(data)} items")
                                    break
                            except:
                                pass

            if rankings:
                df = pd.DataFrame(rankings)
                df = df.drop_duplicates()
                df.to_csv(output_dir / 'corporate_knights_global100.csv', index=False)
                print(f"Saved {len(df)} rankings to data/esg_scores/corporate_knights_global100.csv")

                # Show sample
                print("\nSample rankings:")
                print(df.head(10).to_string(index=False))

                return df
            else:
                print("No rankings extracted. Saving HTML for manual inspection...")
                with open(output_dir / 'corporate_knights_page.html', 'w') as f:
                    f.write(resp.text)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return None


def scrape_fortune_admired():
    """Scrape Fortune World's Most Admired Companies."""
    print("\n" + "=" * 60)
    print("FORTUNE MOST ADMIRED COMPANIES")
    print("=" * 60)

    url = "https://fortune.com/ranking/worlds-most-admired-companies/"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            rankings = []

            # Method 1: Look for ranking list items
            list_items = soup.find_all('li')
            print(f"Found {len(list_items)} list items")

            # Method 2: Look for company cards
            cards = soup.find_all(['div', 'article'], class_=re.compile(r'company|rank|card'))
            print(f"Found {len(cards)} card elements")

            # Method 3: Look for JSON-LD or embedded data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if 'itemListElement' in data:
                        for item in data['itemListElement']:
                            rankings.append({
                                'rank': item.get('position'),
                                'company': item.get('name') or item.get('item', {}).get('name'),
                                'source': 'Fortune Most Admired'
                            })
                except:
                    pass

            # Method 4: Look for Next.js or React hydration data
            for script in soup.find_all('script'):
                if script.string and '__NEXT_DATA__' in str(script.string):
                    try:
                        json_text = re.search(r'__NEXT_DATA__\s*=\s*({.*?})\s*;', script.string)
                        if json_text:
                            data = json.loads(json_text.group(1))
                            print(f"Found Next.js data")
                    except:
                        pass

            # Method 5: Parse visible text
            if not rankings:
                # Find ranking patterns in text
                text = soup.get_text()
                lines = text.split('\n')

                for i, line in enumerate(lines):
                    line = line.strip()
                    # Look for numbered entries
                    match = re.match(r'^(\d+)\.\s+(.+)$', line)
                    if match and int(match.group(1)) <= 500:
                        company = match.group(2).strip()
                        if len(company) > 2 and company[0].isupper():
                            rankings.append({
                                'rank': int(match.group(1)),
                                'company': company,
                                'source': 'Fortune Most Admired'
                            })

            if rankings:
                df = pd.DataFrame(rankings)
                df = df.drop_duplicates()
                df.to_csv(output_dir / 'fortune_most_admired.csv', index=False)
                print(f"Saved {len(df)} rankings to data/esg_scores/fortune_most_admired.csv")
                print("\nSample rankings:")
                print(df.head(10).to_string(index=False))
                return df
            else:
                print("No rankings extracted. Saving HTML for inspection...")
                with open(output_dir / 'fortune_admired_page.html', 'w') as f:
                    f.write(resp.text)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    return None


def scrape_newsweek_responsible():
    """Scrape Newsweek America's Most Responsible Companies."""
    print("\n" + "=" * 60)
    print("NEWSWEEK MOST RESPONSIBLE COMPANIES")
    print("=" * 60)

    url = "https://www.newsweek.com/rankings/americas-most-responsible-companies-2024"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        print(f"Status: {resp.status_code}")

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')

            rankings = []

            # Look for table rows
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables")

            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        text = [c.get_text(strip=True) for c in cells]
                        if text[0].isdigit():
                            rankings.append({
                                'rank': int(text[0]),
                                'company': text[1],
                                'industry': text[2] if len(text) > 2 else '',
                                'score': text[-1] if len(text) > 3 else '',
                                'source': 'Newsweek Most Responsible'
                            })

            if rankings:
                df = pd.DataFrame(rankings)
                df.to_csv(output_dir / 'newsweek_responsible.csv', index=False)
                print(f"Saved {len(df)} rankings")
                print("\nSample rankings:")
                print(df.head(10).to_string(index=False))
                return df
            else:
                print("No table data found. Saving HTML...")
                with open(output_dir / 'newsweek_page.html', 'w') as f:
                    f.write(resp.text)

    except Exception as e:
        print(f"Error: {e}")

    return None


def compile_existing_data():
    """Compile all existing ESG data we've collected."""
    print("\n" + "=" * 60)
    print("COMPILING EXISTING ESG DATA")
    print("=" * 60)

    # Load Kaggle Sustainalytics data
    kaggle_path = project_root / 'data' / 'kaggle_esg' / 'SP 500 ESG Risk Ratings.csv'
    if kaggle_path.exists():
        kaggle_df = pd.read_csv(kaggle_path)
        print(f"Kaggle Sustainalytics: {len(kaggle_df)} firms")
    else:
        kaggle_df = None
        print("Kaggle data not found")

    # Load manual Big Tech panel
    big_tech_path = output_dir / 'big_tech_esg_manual.csv'
    if big_tech_path.exists():
        big_tech_df = pd.read_csv(big_tech_path)
        print(f"Big Tech manual panel: {len(big_tech_df)} observations")
    else:
        big_tech_df = None
        print("Big Tech panel not found")

    # Summarize Big Tech ESG from Kaggle
    if kaggle_df is not None:
        big_tech_tickers = ['MSFT', 'AAPL', 'GOOGL', 'AMZN', 'META', 'NVDA']

        print("\n" + "-" * 40)
        print("BIG TECH ESG RISK SCORES (Sustainalytics)")
        print("-" * 40)

        # Check which column contains ticker
        ticker_col = None
        for col in ['Symbol', 'Ticker', 'ticker', 'symbol']:
            if col in kaggle_df.columns:
                ticker_col = col
                break

        if ticker_col:
            for ticker in big_tech_tickers:
                row = kaggle_df[kaggle_df[ticker_col] == ticker]
                if not row.empty:
                    row = row.iloc[0]
                    # Find relevant columns
                    total_risk = row.get('Total ESG Risk score', row.get('esg_risk_score', 'N/A'))
                    env_risk = row.get('Environment Risk Score', row.get('env_risk', 'N/A'))
                    company = row.get('Name', row.get('Company', ticker))
                    print(f"{ticker:6} ({company[:20]:20}): Total={total_risk}, Env={env_risk}")
        else:
            print("Could not identify ticker column")
            print(f"Available columns: {list(kaggle_df.columns)}")


def main():
    """Run all scrapers."""
    print("ESG DATA COLLECTION FROM FREE SOURCES")
    print("=" * 60)

    # Try all sources
    just_capital = scrape_just_capital_api()
    corporate_knights = scrape_corporate_knights()
    fortune = scrape_fortune_admired()
    newsweek = scrape_newsweek_responsible()

    # Compile existing data
    compile_existing_data()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    sources = [
        ('Just Capital API', just_capital is not None),
        ('Corporate Knights', corporate_knights is not None),
        ('Fortune Most Admired', fortune is not None),
        ('Newsweek Responsible', newsweek is not None),
    ]

    for name, success in sources:
        status = "SUCCESS" if success else "FAILED"
        print(f"  {name:25} {status}")


if __name__ == '__main__':
    # Install beautifulsoup4 if needed
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        os.system("pip3 install beautifulsoup4")
        from bs4 import BeautifulSoup

    main()
