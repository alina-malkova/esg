# Manual Scope 2 Extraction Guide

## Priority List: Top 50 Firms by AI/Data Center Relevance

### Tier 1: AI Infrastructure Builders (15 firms) - HIGHEST PRIORITY
These firms directly own/operate data centers and their Scope 2 is the key outcome variable.

| Ticker | Company | Sustainability Report URL | Status |
|--------|---------|--------------------------|--------|
| MSFT | Microsoft | microsoft.com/sustainability | ✅ Done |
| GOOGL | Alphabet | sustainability.google | ✅ Done |
| META | Meta | sustainability.fb.com | ✅ Done |
| AMZN | Amazon | sustainability.aboutamazon.com | ✅ Done |
| AAPL | Apple | apple.com/environment | ✅ Done |
| NVDA | NVIDIA | nvidia.com/csr | ✅ Done |
| ORCL | Oracle | oracle.com/corporate/citizenship | ⬜ TODO |
| IBM | IBM | ibm.com/impact | ⬜ TODO |
| CRM | Salesforce | salesforce.com/sustainability | ⬜ TODO |
| CSCO | Cisco | cisco.com/csr | ⬜ TODO |
| INTC | Intel | intel.com/sustainability | ⬜ TODO |
| AMD | AMD | amd.com/corporate-responsibility | ⬜ TODO |
| NOW | ServiceNow | servicenow.com/company/global-impact | ⬜ TODO |
| SNOW | Snowflake | snowflake.com/sustainability | ⬜ TODO |
| PLTR | Palantir | palantir.com/impact | ⬜ TODO |

### Tier 2: Data Center REITs (5 firms)
Pure-play data center operators - their entire business is Scope 2.

| Ticker | Company | Sustainability Report URL | Status |
|--------|---------|--------------------------|--------|
| EQIX | Equinix | equinix.com/sustainability | ⬜ TODO |
| DLR | Digital Realty | digitalrealty.com/sustainability | ⬜ TODO |
| AMT | American Tower | americantower.com/sustainability | ⬜ TODO |
| CCI | Crown Castle | crowncastle.com/responsibility | ⬜ TODO |
| SBAC | SBA Communications | sbasite.com/responsibility | ⬜ TODO |

### Tier 3: High AI Exposure (Financials/Tech Services, 15 firms)
These sectors have highest AI exposure index but may be users, not builders.

| Ticker | Company | Sector | Status |
|--------|---------|--------|--------|
| JPM | JPMorgan Chase | Financials | ⬜ TODO |
| BAC | Bank of America | Financials | ⬜ TODO |
| GS | Goldman Sachs | Financials | ⬜ TODO |
| MS | Morgan Stanley | Financials | ⬜ TODO |
| C | Citigroup | Financials | ⬜ TODO |
| V | Visa | Financials | ⬜ TODO |
| MA | Mastercard | Financials | ⬜ TODO |
| PYPL | PayPal | Financials | ⬜ TODO |
| BLK | BlackRock | Financials | ⬜ TODO |
| SCHW | Charles Schwab | Financials | ⬜ TODO |
| ADBE | Adobe | Technology | ⬜ TODO |
| ACN | Accenture | Technology | ⬜ TODO |
| INTU | Intuit | Technology | ⬜ TODO |
| PANW | Palo Alto Networks | Technology | ⬜ TODO |
| UBER | Uber | Technology | ⬜ TODO |

### Tier 4: Control Group - Low AI Exposure (15 firms)
Traditional industries for comparison.

| Ticker | Company | Sector | Status |
|--------|---------|--------|--------|
| XOM | Exxon Mobil | Energy | ⬜ TODO |
| CVX | Chevron | Energy | ⬜ TODO |
| COP | ConocoPhillips | Energy | ⬜ TODO |
| NEE | NextEra Energy | Utilities | ⬜ TODO |
| DUK | Duke Energy | Utilities | ⬜ TODO |
| SO | Southern Company | Utilities | ⬜ TODO |
| CAT | Caterpillar | Industrials | ⬜ TODO |
| DE | Deere & Co | Industrials | ⬜ TODO |
| LMT | Lockheed Martin | Industrials | ⬜ TODO |
| PG | Procter & Gamble | Consumer Staples | ⬜ TODO |
| KO | Coca-Cola | Consumer Staples | ⬜ TODO |
| PEP | PepsiCo | Consumer Staples | ⬜ TODO |
| WMT | Walmart | Consumer Staples | ⬜ TODO |
| HD | Home Depot | Consumer Discretionary | ⬜ TODO |
| MCD | McDonald's | Consumer Discretionary | ⬜ TODO |

---

## Extraction Protocol

### Step 1: Find Sustainability Report
- Search "[Company] sustainability report 2023"
- Look for "Environmental Data" or "GHG Emissions" section
- Most reports are PDF format

### Step 2: Extract Data Points
For each year (2019-2023), extract:

1. **Scope 1** (Direct emissions) - MT CO2e
2. **Scope 2 Location-Based** - MT CO2e (REQUIRED)
3. **Scope 2 Market-Based** - MT CO2e (if available)
4. **Total Scope 1+2** - MT CO2e

### Step 3: Data Quality Notes
- Record the source URL
- Note any methodology changes
- Flag estimated vs. audited data
- Note if data is calendar year vs. fiscal year

### Step 4: Enter in Template
Add to `top50_scope2_template.csv`

---

## Expected Time Estimate

| Tier | Firms | Est. Time/Firm | Total |
|------|-------|----------------|-------|
| Tier 1 (remaining) | 9 | 30 min | 4.5 hrs |
| Tier 2 (REITs) | 5 | 30 min | 2.5 hrs |
| Tier 3 (Financials) | 15 | 20 min | 5 hrs |
| Tier 4 (Control) | 15 | 20 min | 5 hrs |
| **TOTAL** | **44** | — | **~17 hrs** |

Note: Big Tech (6 firms) already done = 6 x 30 min = 3 hrs already saved.

---

## Alternative: Research Assistant Task

This is an ideal task for a research assistant. Provide them with:
1. This guide
2. The template CSV
3. Access to company sustainability reports

Estimated RA time: 15-20 hours
