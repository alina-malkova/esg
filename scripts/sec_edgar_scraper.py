"""
SEC EDGAR 10-K Scraper for AI Keyword Extraction
Extracts AI adoption intensity from annual reports
"""

import os
import re
import time
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data" / "sec_filings"

# SEC requires user-agent header
HEADERS = {
    'User-Agent': 'Academic Research amalkova@fit.edu',
    'Accept-Encoding': 'gzip, deflate',
}

# AI-related keywords for text analysis
AI_KEYWORDS = [
    'artificial intelligence',
    'machine learning',
    'deep learning',
    'neural network',
    'natural language processing',
    'computer vision',
    'generative ai',
    'large language model',
    'chatgpt',
    'automation',
    'algorithmic',
    'predictive analytics',
    'data science',
    'ai-powered',
    'ai-driven',
    'intelligent automation',
]

def get_cik_from_ticker(ticker):
    """Get CIK number from ticker symbol using SEC mapping"""
    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        for entry in data.values():
            if entry['ticker'].upper() == ticker.upper():
                return str(entry['cik_str']).zfill(10)
    except Exception as e:
        print(f"Error getting CIK for {ticker}: {e}")
    return None

def get_10k_filings(cik, start_year=2018):
    """Get list of 10-K filings for a company"""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        filings = []
        recent = data.get('filings', {}).get('recent', {})

        for i in range(len(recent.get('form', []))):
            form = recent['form'][i]
            if form in ['10-K', '10-K/A']:
                filing_date = recent['filingDate'][i]
                year = int(filing_date[:4])
                if year >= start_year:
                    filings.append({
                        'form': form,
                        'date': filing_date,
                        'accession': recent['accessionNumber'][i].replace('-', ''),
                        'primary_doc': recent['primaryDocument'][i]
                    })
        return filings
    except Exception as e:
        print(f"Error getting filings for CIK {cik}: {e}")
        return []

def download_10k_text(cik, accession, primary_doc):
    """Download and extract text from 10-K filing"""
    url = f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession}/{primary_doc}"
    try:
        time.sleep(0.1)  # SEC rate limit: 10 requests/second
        response = requests.get(url, headers=HEADERS)
        text = response.text

        # Remove HTML tags for cleaner text analysis
        clean_text = re.sub(r'<[^>]+>', ' ', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).lower()

        return clean_text
    except Exception as e:
        print(f"Error downloading filing: {e}")
        return ""

def count_ai_keywords(text):
    """Count AI-related keywords in document text"""
    counts = {}
    total = 0

    for keyword in AI_KEYWORDS:
        count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE))
        counts[keyword] = count
        total += count

    return counts, total

def process_company(ticker, start_year=2018):
    """Process all 10-K filings for a company"""
    print(f"\nProcessing {ticker}...")

    cik = get_cik_from_ticker(ticker)
    if not cik:
        print(f"  Could not find CIK for {ticker}")
        return []

    filings = get_10k_filings(cik, start_year)
    print(f"  Found {len(filings)} 10-K filings since {start_year}")

    results = []
    for filing in filings:
        print(f"  Processing {filing['date']}...")
        text = download_10k_text(cik, filing['accession'], filing['primary_doc'])

        if text:
            word_count = len(text.split())
            keyword_counts, total_keywords = count_ai_keywords(text)

            result = {
                'ticker': ticker,
                'cik': cik,
                'filing_date': filing['date'],
                'filing_year': int(filing['date'][:4]),
                'word_count': word_count,
                'total_ai_keywords': total_keywords,
                'ai_intensity': total_keywords / word_count * 10000 if word_count > 0 else 0,  # per 10k words
            }
            result.update(keyword_counts)
            results.append(result)

    return results

def main():
    """Process sample of S&P 500 firms"""
    print("="*60)
    print("SEC EDGAR 10-K AI Keyword Scraper")
    print("="*60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load S&P 500 list
    sp500_file = BASE_DIR / "data" / "sp500_constituents.csv"
    if sp500_file.exists():
        sp500 = pd.read_csv(sp500_file)
        tickers = sp500['Symbol'].tolist()  # All S&P 500 companies
    else:
        # Default sample of diverse firms
        tickers = [
            'GOOGL', 'MSFT', 'META', 'AMZN', 'AAPL',  # Tech
            'JPM', 'BAC', 'GS', 'WFC',  # Finance
            'JNJ', 'PFE', 'UNH',  # Healthcare
            'XOM', 'CVX',  # Energy
            'WMT', 'HD', 'COST',  # Retail
            'BA', 'CAT', 'GE',  # Industrial
        ]

    print(f"Processing {len(tickers)} companies...")

    all_results = []
    for i, ticker in enumerate(tickers):
        print(f"\n[{i+1}/{len(tickers)}]", end="")
        try:
            results = process_company(ticker)
            all_results.extend(results)

            # Save incrementally
            if (i + 1) % 10 == 0:
                df = pd.DataFrame(all_results)
                df.to_csv(DATA_DIR / "ai_keywords_10k_partial.csv", index=False)
                print(f"\n  Saved checkpoint: {len(all_results)} records")

        except Exception as e:
            print(f"  Error processing {ticker}: {e}")

        time.sleep(0.5)  # Be nice to SEC servers

    # Save final results
    df = pd.DataFrame(all_results)
    df.to_csv(DATA_DIR / "ai_keywords_10k.csv", index=False)
    print(f"\n\nSaved: {DATA_DIR / 'ai_keywords_10k.csv'}")
    print(f"Total records: {len(df)}")

    # Summary statistics
    print("\n=== Summary ===")
    print(df.groupby('filing_year')['ai_intensity'].describe())

if __name__ == "__main__":
    main()
