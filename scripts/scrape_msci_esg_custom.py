#!/usr/bin/env python3
"""
Custom MSCI ESG Rating Scraper
Direct Selenium scraper for MSCI's ESG Ratings Corporate Search Tool.

The MSCI tool shows current ESG letter rating (AAA to CCC) plus rating history.
This script extracts both current ratings and historical rating changes.

Usage:
    python scripts/scrape_msci_esg_custom.py [--test] [--batch N]
"""

import pandas as pd
import json
import time
import re
import os
import sys
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Set up paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
OUTPUT_DIR = DATA_DIR / 'msci_esg'
OUTPUT_DIR.mkdir(exist_ok=True)

RATINGS_FILE = OUTPUT_DIR / 'msci_esg_ratings_custom.csv'
HISTORY_FILE = OUTPUT_DIR / 'msci_esg_history.csv'
CHECKPOINT_FILE = OUTPUT_DIR / 'scrape_checkpoint_custom.json'
ERROR_LOG = OUTPUT_DIR / 'scrape_errors_custom.log'

MSCI_SEARCH_URL = "https://www.msci.com/our-solutions/esg-investing/esg-ratings-corporate-search-tool"


def setup_driver(headless=True):
    """Set up Chrome WebDriver with appropriate options."""
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


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
    return {'completed': [], 'failed': [], 'ratings': [], 'history': []}


def save_checkpoint(checkpoint):
    """Save scraping checkpoint."""
    checkpoint['last_updated'] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(checkpoint, f, indent=2)


def log_error(ticker, error):
    """Log errors to file."""
    with open(ERROR_LOG, 'a') as f:
        f.write(f"{datetime.now().isoformat()} | {ticker} | {error}\n")


def accept_cookies(driver):
    """Accept cookies popup if present."""
    try:
        cookie_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_btn.click()
        time.sleep(1)
    except TimeoutException:
        pass  # No cookie popup


def search_company(driver, ticker, company_name):
    """Search for a company on MSCI's ESG tool."""
    # Navigate to search page
    driver.get(MSCI_SEARCH_URL)
    time.sleep(2)

    # Accept cookies on first visit
    accept_cookies(driver)

    # Find search input - MSCI uses different possible selectors
    search_selectors = [
        "input[placeholder*='Search']",
        "input[type='search']",
        "#esg-ratings-search-input",
        ".search-input",
        "input[name='searchTerm']"
    ]

    search_box = None
    for selector in search_selectors:
        try:
            search_box = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            break
        except TimeoutException:
            continue

    if not search_box:
        raise Exception("Could not find search box")

    # Clear and enter search term
    search_box.clear()
    search_box.send_keys(ticker)
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)

    return driver


def extract_rating(driver, ticker, company_name, sector):
    """Extract ESG rating information from the page."""
    result = {
        'ticker': ticker,
        'company_name': company_name,
        'sector': sector,
        'scrape_date': datetime.now().isoformat()
    }

    # Try to find the rating element
    rating_selectors = [
        ".ratingdata-company-rating",
        "[class*='esg-rating']",
        "[class*='rating-badge']",
        ".company-rating",
        "div[data-rating]"
    ]

    for selector in rating_selectors:
        try:
            rating_elem = driver.find_element(By.CSS_SELECTOR, selector)
            rating_text = rating_elem.text.strip()
            if rating_text in ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC']:
                result['msci_rating'] = rating_text
                break
        except NoSuchElementException:
            continue

    # Try to extract rating history (if chart data is available)
    try:
        # Look for rating history in JavaScript data or chart elements
        history_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='history'], [class*='chart']")
        for elem in history_elements:
            # Try to extract data attributes
            data = elem.get_attribute('data-ratings') or elem.get_attribute('data-history')
            if data:
                result['rating_history_raw'] = data
                break
    except Exception:
        pass

    # Try to get industry classification
    try:
        industry_elem = driver.find_element(By.CSS_SELECTOR, "[class*='industry'], [class*='sector']")
        result['msci_industry'] = industry_elem.text.strip()
    except NoSuchElementException:
        pass

    # Get page URL
    result['source_url'] = driver.current_url

    return result


def scrape_company(driver, ticker, company_name, sector, retries=2):
    """Scrape ESG rating for a single company."""
    for attempt in range(retries + 1):
        try:
            search_company(driver, ticker, company_name)
            result = extract_rating(driver, ticker, company_name, sector)

            if result.get('msci_rating'):
                return result

            # If no rating found, try searching by company name
            if attempt == 0:
                search_company(driver, company_name.split()[0], company_name)
                result = extract_rating(driver, ticker, company_name, sector)
                if result.get('msci_rating'):
                    return result

            time.sleep(2)

        except Exception as e:
            if attempt < retries:
                time.sleep(3)
            else:
                log_error(ticker, str(e))
                return None

    return None


def scrape_all_ratings(test_mode=False, batch_size=None, headless=True):
    """Main scraping function."""
    print("=" * 60)
    print("MSCI ESG Rating Scraper (Custom)")
    print("=" * 60)

    # Load companies
    companies = load_sp500_tickers()
    print(f"Loaded {len(companies)} S&P 500 companies")

    if test_mode:
        test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'META', 'TSLA']
        companies = [c for c in companies if c['Symbol'] in test_tickers]
        print(f"TEST MODE: {len(companies)} companies")

    if batch_size:
        companies = companies[:batch_size]
        print(f"BATCH MODE: {len(companies)} companies")

    # Load checkpoint
    checkpoint = load_checkpoint()
    companies = [c for c in companies if c['Symbol'] not in checkpoint['completed']]
    print(f"Remaining: {len(companies)} companies")

    # Set up driver
    print("\nInitializing Chrome WebDriver...")
    driver = setup_driver(headless=headless)

    print(f"\nStarting scrape...")
    print("-" * 60)

    try:
        for i, company in enumerate(companies, 1):
            ticker = company['Symbol']
            name = company['Security']
            sector = company['GICS Sector']

            print(f"[{i}/{len(companies)}] {ticker} ({name})...", end=' ', flush=True)

            result = scrape_company(driver, ticker, name, sector)

            if result and result.get('msci_rating'):
                checkpoint['ratings'].append(result)
                checkpoint['completed'].append(ticker)
                print(f"OK - {result['msci_rating']}")
            else:
                checkpoint['failed'].append(ticker)
                print("NO DATA")

            # Save checkpoint every 10 companies
            if i % 10 == 0:
                save_checkpoint(checkpoint)
                if checkpoint['ratings']:
                    pd.DataFrame(checkpoint['ratings']).to_csv(RATINGS_FILE, index=False)

            time.sleep(2)  # Rate limiting

    finally:
        driver.quit()

    # Final save
    save_checkpoint(checkpoint)
    if checkpoint['ratings']:
        df = pd.DataFrame(checkpoint['ratings'])
        df.to_csv(RATINGS_FILE, index=False)

    # Summary
    print("\n" + "=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)
    print(f"Successfully scraped: {len(checkpoint['completed'])} companies")
    print(f"No data: {len(checkpoint['failed'])} companies")

    if checkpoint['ratings']:
        df = pd.DataFrame(checkpoint['ratings'])
        print(f"\nRating Distribution:")
        print(df['msci_rating'].value_counts().sort_index())

    return checkpoint['ratings']


if __name__ == '__main__':
    args = sys.argv[1:]

    test_mode = '--test' in args
    headless = '--visible' not in args
    batch_size = None

    if '--batch' in args:
        idx = args.index('--batch')
        if idx + 1 < len(args):
            batch_size = int(args[idx + 1])

    scrape_all_ratings(test_mode=test_mode, batch_size=batch_size, headless=headless)
