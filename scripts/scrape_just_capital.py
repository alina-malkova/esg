#!/usr/bin/env python3
"""
Scrape Just Capital ESG rankings for S&P 500 companies.
Uses Selenium with improved parsing for the rankings table.
"""

import os
import sys
import time
import re
import json
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def scrape_just_capital_rankings():
    """Scrape Just Capital 2024 rankings using Selenium."""

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("Installing selenium...")
        os.system("pip3 install selenium webdriver-manager")
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

    print("Setting up Chrome driver...")

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    rankings = []

    try:
        url = "https://justcapital.com/rankings/"
        print(f"Loading {url}...")
        driver.get(url)

        # Wait for page to load
        time.sleep(5)

        # Try to find ranking table rows
        print("Looking for ranking elements...")

        # Try multiple selectors
        selectors = [
            "table tbody tr",
            ".ranking-row",
            "[class*='ranking']",
            "tr[data-rank]",
            ".company-row",
            "[class*='company']"
        ]

        rows = []
        for selector in selectors:
            try:
                rows = driver.find_elements(By.CSS_SELECTOR, selector)
                if rows:
                    print(f"Found {len(rows)} elements with selector: {selector}")
                    break
            except:
                continue

        # If no structured elements, parse the page source
        if not rows:
            print("No structured elements found. Parsing page source...")
            page_source = driver.page_source

            # Save page source for debugging
            with open(project_root / 'data' / 'esg_scores' / 'just_capital_page.html', 'w') as f:
                f.write(page_source)
            print("Page source saved to data/esg_scores/just_capital_page.html")

            # Try to extract company rankings from text
            # Pattern: look for numbered list with company names

            # Pattern 1: #1 Company Name (Industry)
            pattern1 = r'#(\d+)\s+([A-Za-z][A-Za-z0-9\s\.\-&,\']+?)(?:\s*[\(\|]\s*([A-Za-z\s&]+)\s*[\)\|])?(?:\s*(?:#\d+|$))'

            # Pattern 2: Table-like structure with rank, company, industry
            pattern2 = r'(\d+)\.\s*([A-Za-z][A-Za-z0-9\s\.\-&,\']+?)\s+(?:Score:?\s*)?(\d+\.?\d*)?'

            # Pattern 3: Company names in specific divs or spans
            text = driver.find_element(By.TAG_NAME, 'body').text
            lines = text.split('\n')

            print(f"Total text lines: {len(lines)}")

            # Look for ranking patterns in text
            current_rank = 0
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue

                # Check for rank number at start
                rank_match = re.match(r'^(\d+)\.?\s*$', line)
                if rank_match:
                    current_rank = int(rank_match.group(1))
                    continue

                # Check for company name after rank
                if current_rank > 0 and len(line) > 2 and line[0].isupper():
                    # This might be a company name
                    # Check next line for industry
                    industry = ''
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line and not re.match(r'^\d+\.?\s*$', next_line):
                            if len(next_line) < 50:  # Industry names are typically short
                                industry = next_line

                    rankings.append({
                        'rank': current_rank,
                        'company': line,
                        'industry': industry
                    })
                    current_rank = 0

            # Alternative: Look for specific Just Capital ranking patterns
            if not rankings:
                print("Trying alternative parsing...")

                # Try to find ranking cards or list items
                cards = driver.find_elements(By.CSS_SELECTOR, '[class*="card"], [class*="item"], li')

                for card in cards[:500]:  # Limit to avoid timeout
                    try:
                        text = card.text.strip()
                        if not text:
                            continue

                        # Look for rank and company pattern
                        match = re.search(r'(?:^|#)(\d+)\s+(.+)', text)
                        if match:
                            rank = int(match.group(1))
                            rest = match.group(2).strip()

                            # Split company and industry if present
                            if '\n' in rest:
                                parts = rest.split('\n')
                                company = parts[0].strip()
                                industry = parts[1].strip() if len(parts) > 1 else ''
                            else:
                                company = rest
                                industry = ''

                            if rank <= 1000 and len(company) > 2:
                                rankings.append({
                                    'rank': rank,
                                    'company': company,
                                    'industry': industry
                                })
                    except:
                        continue

        else:
            # Parse structured rows
            for row in rows:
                try:
                    text = row.text.strip()
                    cells = row.find_elements(By.TAG_NAME, 'td')

                    if cells and len(cells) >= 2:
                        rank_text = cells[0].text.strip()
                        company_text = cells[1].text.strip()
                        industry_text = cells[2].text.strip() if len(cells) > 2 else ''

                        rank_match = re.search(r'(\d+)', rank_text)
                        if rank_match:
                            rankings.append({
                                'rank': int(rank_match.group(1)),
                                'company': company_text,
                                'industry': industry_text
                            })
                except:
                    continue

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()

    # Remove duplicates and sort
    if rankings:
        df = pd.DataFrame(rankings)
        df = df.drop_duplicates(subset=['rank', 'company'])
        df = df.sort_values('rank')

        print(f"\nExtracted {len(df)} rankings")

        # Save to CSV
        output_path = project_root / 'data' / 'esg_scores' / 'just_capital_rankings.csv'
        df.to_csv(output_path, index=False)
        print(f"Saved to {output_path}")

        # Show Big Tech rankings
        big_tech = ['Microsoft', 'Apple', 'Alphabet', 'Google', 'Amazon', 'Meta', 'Facebook', 'NVIDIA', 'Nvidia']
        print("\nBIG TECH RANKINGS:")
        print("-" * 60)

        for _, row in df.iterrows():
            company_lower = row['company'].lower()
            for tech in big_tech:
                if tech.lower() in company_lower:
                    print(f"  #{row['rank']}: {row['company']} ({row['industry']})")
                    break

        # Show top 20
        print("\nTOP 20 COMPANIES:")
        print("-" * 60)
        for _, row in df.head(20).iterrows():
            print(f"  #{row['rank']}: {row['company']} ({row['industry']})")

        return df
    else:
        print("No rankings extracted")
        return None


def scrape_just_capital_api():
    """Try to find and use Just Capital API endpoints."""

    import requests

    # Common API endpoints to try
    endpoints = [
        "https://justcapital.com/api/rankings",
        "https://justcapital.com/api/v1/rankings",
        "https://justcapital.com/api/companies",
        "https://api.justcapital.com/rankings",
        "https://justcapital.com/wp-json/wp/v2/rankings",
        "https://justcapital.com/wp-json/justcapital/v1/rankings"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        'Accept': 'application/json'
    }

    print("\nTrying API endpoints...")

    for endpoint in endpoints:
        try:
            resp = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  {endpoint}: {resp.status_code}")

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print(f"    Got JSON response with {len(data) if isinstance(data, list) else 'dict'} items")
                    return data
                except:
                    pass
        except Exception as e:
            print(f"  {endpoint}: Error - {str(e)[:50]}")

    return None


def try_alternative_sources():
    """Try other free ESG ranking sources."""

    import requests

    sources = []

    # Source 1: Corporate Knights Global 100
    print("\n1. Trying Corporate Knights Global 100...")
    try:
        resp = requests.get(
            "https://www.corporateknights.com/rankings/global-100-rankings/",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15
        )
        if resp.status_code == 200:
            print(f"   Accessible! (Status {resp.status_code}, {len(resp.text)} chars)")
            sources.append(('Corporate Knights', resp.text))
        else:
            print(f"   Status {resp.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    # Source 2: Fortune World's Most Admired
    print("\n2. Trying Fortune Most Admired...")
    try:
        resp = requests.get(
            "https://fortune.com/ranking/worlds-most-admired-companies/",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15
        )
        if resp.status_code == 200:
            print(f"   Accessible! (Status {resp.status_code}, {len(resp.text)} chars)")
            sources.append(('Fortune', resp.text))
        else:
            print(f"   Status {resp.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    # Source 3: Wikipedia's list of largest companies by ESG
    print("\n3. Trying Wikipedia ESG lists...")
    try:
        resp = requests.get(
            "https://en.wikipedia.org/wiki/Environmental,_social,_and_corporate_governance",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=15
        )
        if resp.status_code == 200:
            print(f"   Accessible! (Status {resp.status_code})")
        else:
            print(f"   Status {resp.status_code}")
    except Exception as e:
        print(f"   Error: {e}")

    return sources


if __name__ == '__main__':
    # Try API first
    api_data = scrape_just_capital_api()

    if not api_data:
        # Fall back to Selenium scraping
        rankings = scrape_just_capital_rankings()

    # Also try alternative sources
    print("\n" + "=" * 60)
    print("CHECKING ALTERNATIVE SOURCES")
    print("=" * 60)
    try_alternative_sources()
