#!/usr/bin/env python3
"""
MSCI ESG Rating Scraper
Collects ESG ratings from MSCI's free search tool for S&P 500 companies.
Uses the py-msci-esg package with Selenium automation.

Usage:
    python scripts/scrape_msci_esg.py [--test] [--resume] [--batch N]

Options:
    --test      Test with 5 sample companies first
    --resume    Resume from last checkpoint
    --batch N   Process N companies at a time (default: all)
"""

import pandas as pd
import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR / 'msci_esg'
OUTPUT_DIR.mkdir(exist_ok=True)

# Output files
RATINGS_FILE = OUTPUT_DIR / 'msci_esg_ratings.csv'
RATINGS_JSON = OUTPUT_DIR / 'msci_esg_ratings.json'
CHECKPOINT_FILE = OUTPUT_DIR / 'scrape_checkpoint.json'
ERROR_LOG = OUTPUT_DIR / 'scrape_errors.log'


def load_sp500_tickers():
    """Load S&P 500 tickers from CSV."""
    sp500_file = DATA_DIR / 'sp500_constituents.csv'
    df = pd.read_csv(sp500_file)
    return df[['Symbol', 'Security', 'GICS Sector']].to_dict('records')


def load_checkpoint():
    """Load scraping checkpoint if it exists."""
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {'completed': [], 'failed': [], 'last_updated': None}


def save_checkpoint(checkpoint):
    """Save scraping checkpoint."""
    checkpoint['last_updated'] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)


def log_error(ticker, error):
    """Log errors to file."""
    with open(ERROR_LOG, 'a') as f:
        f.write(f"{datetime.now().isoformat()} | {ticker} | {error}\n")


def scrape_msci_rating(finder, ticker, company_name, sector, retries=2):
    """
    Scrape MSCI ESG rating for a single company.
    Returns dict with rating info or None on failure.
    """
    for attempt in range(retries + 1):
        try:
            # Get ESG rating from MSCI
            result = finder.get_esg_rating(symbol=ticker, js_timeout=3)

            if result and result.get('rating'):
                return {
                    'ticker': ticker,
                    'company_name': company_name,
                    'sector': sector,
                    'msci_rating': result.get('rating'),
                    'msci_rating_category': result.get('rating_category'),
                    'industry': result.get('industry'),
                    'company_url': result.get('company_url'),
                    'scrape_date': datetime.now().isoformat(),
                    'raw_response': json.dumps(result)
                }

            if attempt < retries:
                time.sleep(2)

        except Exception as e:
            if attempt < retries:
                time.sleep(3)
            else:
                log_error(ticker, str(e))

    return None


def scrape_all_ratings(test_mode=False, resume=False, batch_size=None):
    """
    Main scraping function.
    """
    from msci_esg.ratefinder import ESGRateFinder

    print("=" * 60)
    print("MSCI ESG Rating Scraper")
    print("=" * 60)

    # Load company list
    companies = load_sp500_tickers()
    print(f"Loaded {len(companies)} S&P 500 companies")

    # Test mode - only process a few
    if test_mode:
        test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'META', 'TSLA']
        companies = [c for c in companies if c['Symbol'] in test_tickers]
        print(f"TEST MODE: Processing {len(companies)} companies")

    # Resume from checkpoint
    checkpoint = load_checkpoint() if resume else {'completed': [], 'failed': []}
    if resume and checkpoint['completed']:
        companies = [c for c in companies if c['Symbol'] not in checkpoint['completed']]
        print(f"RESUME MODE: {len(checkpoint['completed'])} already done, {len(companies)} remaining")

    # Apply batch limit
    if batch_size:
        companies = companies[:batch_size]
        print(f"BATCH MODE: Processing {len(companies)} companies")

    # Initialize scraper
    print("\nInitializing Selenium WebDriver...")
    finder = ESGRateFinder(debug=False)

    # Collect results
    results = []

    # Load existing results if resuming
    if resume and RATINGS_FILE.exists():
        existing = pd.read_csv(RATINGS_FILE)
        results = existing.to_dict('records')
        print(f"Loaded {len(results)} existing ratings")

    print(f"\nStarting scrape of {len(companies)} companies...")
    print("-" * 60)

    for i, company in enumerate(companies, 1):
        ticker = company['Symbol']
        name = company['Security']
        sector = company['GICS Sector']

        print(f"[{i}/{len(companies)}] {ticker} ({name})...", end=' ', flush=True)

        result = scrape_msci_rating(finder, ticker, name, sector)

        if result:
            results.append(result)
            checkpoint['completed'].append(ticker)
            print(f"OK - {result['msci_rating']}")
        else:
            checkpoint['failed'].append(ticker)
            print("FAILED")

        # Save checkpoint every 10 companies
        if i % 10 == 0:
            save_checkpoint(checkpoint)
            # Also save intermediate results
            if results:
                df = pd.DataFrame(results)
                df.to_csv(RATINGS_FILE, index=False)

        # Rate limiting - be nice to MSCI servers
        time.sleep(1.5)

    # Final save
    save_checkpoint(checkpoint)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(RATINGS_FILE, index=False)

        # Also save as JSON for easier parsing
        with open(RATINGS_JSON, 'w') as f:
            json.dump(results, f, indent=2)

    # Summary
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successfully scraped: {len(checkpoint['completed'])} companies")
    print(f"Failed: {len(checkpoint['failed'])} companies")
    if checkpoint['failed']:
        print(f"Failed tickers: {', '.join(checkpoint['failed'][:20])}")
        if len(checkpoint['failed']) > 20:
            print(f"  ... and {len(checkpoint['failed']) - 20} more")

    print(f"\nOutput saved to:")
    print(f"  - {RATINGS_FILE}")
    print(f"  - {RATINGS_JSON}")

    # Rating distribution
    if results:
        df = pd.DataFrame(results)
        print("\nRating Distribution:")
        print(df['msci_rating'].value_counts().sort_index())

    return results


def analyze_existing_ratings():
    """Analyze existing scraped ratings."""
    if not RATINGS_FILE.exists():
        print("No ratings file found. Run scraper first.")
        return

    df = pd.read_csv(RATINGS_FILE)

    print("\n" + "=" * 60)
    print("MSCI ESG RATINGS ANALYSIS")
    print("=" * 60)

    print(f"\nTotal companies: {len(df)}")

    print("\n1. Rating Distribution:")
    print(df['msci_rating'].value_counts().sort_index())

    # Map to numeric for analysis
    rating_map = {'CCC': 1, 'B': 2, 'BB': 3, 'BBB': 4, 'A': 5, 'AA': 6, 'AAA': 7}
    df['rating_numeric'] = df['msci_rating'].map(rating_map)

    print("\n2. By Sector:")
    sector_avg = df.groupby('sector')['rating_numeric'].mean().sort_values(ascending=False)
    for sector, avg in sector_avg.items():
        # Convert back to letter
        letter = [k for k, v in rating_map.items() if v == round(avg)][0]
        print(f"  {sector}: {avg:.2f} (~{letter})")

    print("\n3. Rating Categories:")
    print(df['msci_rating_category'].value_counts())

    return df


if __name__ == '__main__':
    args = sys.argv[1:]

    test_mode = '--test' in args
    resume = '--resume' in args
    batch_size = None

    if '--batch' in args:
        idx = args.index('--batch')
        if idx + 1 < len(args):
            batch_size = int(args[idx + 1])

    if '--analyze' in args:
        analyze_existing_ratings()
    else:
        scrape_all_ratings(test_mode=test_mode, resume=resume, batch_size=batch_size)
