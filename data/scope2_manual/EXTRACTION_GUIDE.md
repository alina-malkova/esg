# Manual Scope 2 Extraction Guide

## Priority List: Top 50 Firms by AI/Data Center Relevance

**STATUS: COMPLETE** - All 50 firms extracted (81 company-year observations)

### Tier 1: AI Infrastructure Builders (15 firms) - HIGHEST PRIORITY
These firms directly own/operate data centers and their Scope 2 is the key outcome variable.

| Ticker | Company | Sustainability Report URL | Status |
|--------|---------|--------------------------|--------|
| MSFT | Microsoft | microsoft.com/sustainability | ✅ Done (5 years) |
| GOOGL | Alphabet | sustainability.google | ✅ Done (5 years) |
| META | Meta | sustainability.fb.com | ✅ Done (5 years) |
| AMZN | Amazon | sustainability.aboutamazon.com | ✅ Done (5 years) |
| AAPL | Apple | apple.com/environment | ✅ Done (5 years) |
| NVDA | NVIDIA | nvidia.com/csr | ✅ Done (5 years) |
| ORCL | Oracle | oracle.com/corporate/citizenship | ✅ Done |
| IBM | IBM | ibm.com/impact | ✅ Done (2 years) |
| CRM | Salesforce | salesforce.com/sustainability | ✅ Done |
| CSCO | Cisco | cisco.com/csr | ✅ Done (2 years) |
| INTC | Intel | intel.com/sustainability | ✅ Done (2 years) |
| AMD | AMD | amd.com/corporate-responsibility | ✅ Done (2 years) |
| NOW | ServiceNow | servicenow.com/company/global-impact | ✅ Done (2 years) |
| SNOW | Snowflake | snowflake.com/sustainability | ✅ Done |
| PLTR | Palantir | palantir.com/impact | ✅ Done |

### Tier 2: Data Center REITs (5 firms)
Pure-play data center operators - their entire business is Scope 2.

| Ticker | Company | Sustainability Report URL | Status |
|--------|---------|--------------------------|--------|
| EQIX | Equinix | equinix.com/sustainability | ✅ Done |
| DLR | Digital Realty | digitalrealty.com/sustainability | ✅ Done |
| AMT | American Tower | americantower.com/sustainability | ✅ Done |
| CCI | Crown Castle | crowncastle.com/responsibility | ✅ Done |
| SBAC | SBA Communications | sbasite.com/responsibility | ✅ Done |

### Tier 3: High AI Exposure (Financials/Tech Services, 15 firms)
These sectors have highest AI exposure index but may be users, not builders.

| Ticker | Company | Sector | Status |
|--------|---------|--------|--------|
| JPM | JPMorgan Chase | Financials | ✅ Done |
| BAC | Bank of America | Financials | ✅ Done |
| GS | Goldman Sachs | Financials | ✅ Done |
| MS | Morgan Stanley | Financials | ✅ Done |
| C | Citigroup | Financials | ✅ Done |
| V | Visa | Financials | ✅ Done |
| MA | Mastercard | Financials | ✅ Done |
| PYPL | PayPal | Financials | ✅ Done |
| BLK | BlackRock | Financials | ✅ Done |
| SCHW | Charles Schwab | Financials | ✅ Done |
| ADBE | Adobe | Technology | ✅ Done (2 years) |
| ACN | Accenture | Technology | ✅ Done |
| INTU | Intuit | Technology | ✅ Done |
| PANW | Palo Alto Networks | Technology | ✅ Done |
| UBER | Uber | Technology | ✅ Done |

### Tier 4: Control Group - Low AI Exposure (15 firms)
Traditional industries for comparison.

| Ticker | Company | Sector | Status |
|--------|---------|--------|--------|
| XOM | Exxon Mobil | Energy | ✅ Done (2 years) |
| CVX | Chevron | Energy | ✅ Done |
| COP | ConocoPhillips | Energy | ✅ Done |
| NEE | NextEra Energy | Utilities | ✅ Done |
| DUK | Duke Energy | Utilities | ✅ Done |
| SO | Southern Company | Utilities | ✅ Done |
| CAT | Caterpillar | Industrials | ✅ Done |
| DE | Deere & Co | Industrials | ✅ Done |
| LMT | Lockheed Martin | Industrials | ✅ Done |
| PG | Procter & Gamble | Consumer Staples | ✅ Done |
| KO | Coca-Cola | Consumer Staples | ✅ Done |
| PEP | PepsiCo | Consumer Staples | ✅ Done |
| WMT | Walmart | Consumer Staples | ✅ Done |
| HD | Home Depot | Consumer Discretionary | ✅ Done |
| MCD | McDonald's | Consumer Discretionary | ✅ Done |

---

## Dataset Summary

| Metric | Value |
|--------|-------|
| **Unique Companies** | 50 |
| **Total Observations** | 81 |
| **Companies with Multi-Year Data** | 12 |
| **Key AI Infrastructure Builders** | 6 (MSFT, GOOGL, META, AMZN, AAPL, NVDA) with 5-year panels |

### Sector Distribution

| Sector | Companies | Key Finding |
|--------|-----------|-------------|
| Technology | 18 | AI builders show 60-115% Scope 2 growth (2019-2023) |
| Financials | 10 | Low operational footprint; most emissions from Scope 3 |
| Energy | 3 | High Scope 1 dominates (91M MT for XOM) |
| Utilities | 3 | High Scope 1 from power generation |
| Real Estate (REITs) | 5 | Data center REITs heavily Scope 2 dependent |
| Consumer | 7 | Mixed Scope 1/2 profiles |
| Industrials | 4 | Manufacturing-driven emissions |

---

## Data Quality Notes

### High Confidence (Third-Party Verified)
- MSFT, GOOGL, META, AMZN, AAPL, NVDA (Big Tech with detailed sustainability reports)
- JPM, BAC, GS, MS, C (Large financials with CDP disclosures)
- XOM, CVX, COP (Energy majors with regulatory reporting)

### Medium Confidence (Self-Reported)
- Most Technology and Consumer companies
- Data center REITs

### Estimates Applied
- SBAC, SCHW, SNOW: Limited public disclosure; estimated from sector averages
- PANW: Estimated from similar cybersecurity companies
- Some companies report market-based only (converted using grid emission factors)

---

## Extraction Completed

**Date:** February 13, 2026
**Method:** Web searches of corporate sustainability reports, CDP disclosures, ESG databases
**Primary Sources:** Company sustainability reports, CDP Climate responses, Sustainalytics, DitchCarbon

