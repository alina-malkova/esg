"""
Yahoo Finance ESG Score Scraper
Extracts Sustainalytics ESG risk ratings from Yahoo Finance
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
import time

BASE_DIR = Path("/Users/amalkova/Library/CloudStorage/OneDrive-FloridaInstituteofTechnology/Research")
DATA_DIR = BASE_DIR / "data" / "esg_scores"

def get_esg_scores(ticker):
    """Get ESG scores for a single ticker from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)

        # Get sustainability data
        sustainability = stock.sustainability

        if sustainability is not None and not sustainability.empty:
            # Extract key ESG metrics
            result = {
                'ticker': ticker,
                'timestamp': pd.Timestamp.now(),
            }

            # Common sustainability metrics
            metrics = [
                'totalEsg', 'environmentScore', 'socialScore', 'governanceScore',
                'esgPerformance', 'peerGroup', 'peerCount',
                'highestControversy', 'percentile'
            ]

            for metric in metrics:
                if metric in sustainability.index:
                    result[metric] = sustainability.loc[metric, 'Value']

            return result

        return None
    except Exception as e:
        print(f"Error getting ESG for {ticker}: {e}")
        return None

def scrape_sp500_esg():
    """Scrape ESG scores for S&P 500 companies"""
    print("="*60)
    print("Yahoo Finance ESG Score Scraper")
    print("="*60)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Load S&P 500 list
    sp500_file = BASE_DIR / "data" / "sp500_constituents.csv"
    if sp500_file.exists():
        sp500 = pd.read_csv(sp500_file)
        tickers = sp500['Symbol'].tolist()
    else:
        print("S&P 500 list not found")
        return

    print(f"Scraping ESG scores for {len(tickers)} companies...")

    results = []
    for i, ticker in enumerate(tickers):
        if (i + 1) % 50 == 0:
            print(f"Progress: {i+1}/{len(tickers)}")

        esg = get_esg_scores(ticker)
        if esg:
            results.append(esg)

        time.sleep(0.3)  # Rate limiting

    # Save results
    df = pd.DataFrame(results)
    df.to_csv(DATA_DIR / "sp500_esg_scores.csv", index=False)
    print(f"\nSaved: {DATA_DIR / 'sp500_esg_scores.csv'}")
    print(f"Successfully scraped: {len(df)} / {len(tickers)} companies")

    # Summary
    if len(df) > 0:
        print("\n=== ESG Score Summary ===")
        for col in ['totalEsg', 'environmentScore', 'socialScore', 'governanceScore']:
            if col in df.columns:
                print(f"{col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")

    return df

def scrape_sample():
    """Quick test on sample tickers"""
    print("Testing ESG scraper on sample tickers...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    test_tickers = ['GOOGL', 'MSFT', 'META', 'AMZN', 'XOM', 'CVX', 'JPM', 'WMT']
    results = []

    for ticker in test_tickers:
        print(f"  {ticker}...", end=" ")
        esg = get_esg_scores(ticker)
        if esg:
            results.append(esg)
            print(f"ESG: {esg.get('totalEsg', 'N/A')}")
        else:
            print("No data")
        time.sleep(0.5)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(DATA_DIR / "test_esg_scores.csv", index=False)
        print(f"\nSaved test results: {len(df)} companies")
        return df

    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        scrape_sp500_esg()
    else:
        scrape_sample()
