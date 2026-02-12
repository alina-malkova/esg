# ESG Data Sources Guide

## Overview

ESG (Environmental, Social, Governance) scores are ratings that measure a company's performance on sustainability and ethical practices. For this research on AI adoption trade-offs, you need:

1. **Environmental (E) scores** - Most relevant for the AI/data center energy channel
2. **Overall ESG scores** - For the composite trade-off analysis
3. **Historical panel data** - To track changes over time (pre/post AI adoption)

---

## Free ESG Data Sources

### 1. S&P Global ESG Scores (Recommended)

**Website:** https://www.spglobal.com/esg/scores/

**What you get free:**
- ESG scores for ~10,000 companies globally
- Scores on 0-100 scale
- Breakdown by E, S, G pillars
- Annual updates

**How to access:**
1. Create free account at spglobal.com
2. Navigate to ESG Scores section
3. Search companies individually or request bulk data via email
4. Can download company-by-company or request academic access

**Limitations:**
- No direct bulk download API
- Need to scrape or request data manually

---

### 2. Sustainalytics (via Yahoo Finance - DEPRECATED)

**Status:** Yahoo Finance removed ESG data access in late 2024

**Alternative:** Morningstar Direct (requires subscription)

---

### 3. MSCI ESG Ratings

**Website:** https://www.msci.com/our-solutions/esg-investing/esg-ratings-climate-search-tool

**What you get free:**
- Current ESG rating (AAA to CCC scale)
- Industry-adjusted scores
- Key ESG issues flagged

**How to access:**
1. Search individual companies on their free tool
2. No bulk download available free
3. Academic access may be available through university

**Limitations:**
- One company at a time
- No historical data free
- Would need to scrape

---

### 4. Refinitiv ESG Scores (via LSEG)

**Website:** https://www.lseg.com/en/data-analytics/sustainable-finance/esg-scores

**Access:** Requires subscription or university WRDS access

---

### 5. CDP Open Data Portal (Recommended for Emissions)

**Website:** https://data.cdp.net/browse

**Direct links:**
- Governance data: https://data.cdp.net/browse?category=Governance
- Climate data: https://data.cdp.net/browse?category=Climate+Change
- Water data: https://data.cdp.net/browse?category=Water

**What you get free:**
- Corporate climate disclosures (Scope 1, 2, 3 emissions)
- CDP letter grades (A to D-)
- Climate targets and progress
- Water usage data
- Downloadable CSV/Excel files

**How to access:**
1. Browse datasets at data.cdp.net
2. Click on dataset to view
3. Export to CSV directly (no registration for public data)
4. Some datasets require free CDP account

**Key datasets:**
- "Corporate Climate Change Questionnaire Responses"
- "Corporate Emissions Data"
- "Climate Change Scores"

---

### 6. CSRHub

**Website:** https://www.csrhub.com/

**What you get free:**
- Aggregated ESG ratings from 700+ sources
- Limited free searches

**Academic program:** May offer data for research

---

## Alternative: Build Your Own E-Score from CDP Data

Since the E (Environmental) pillar is most relevant to your AI energy hypothesis, you can construct your own environmental score from CDP data:

### CDP (Carbon Disclosure Project)

**Website:** https://www.cdp.net/en/data

**Free after registration:**
- Corporate climate disclosures
- Scope 1, 2, 3 emissions
- Climate targets and progress
- Water usage
- CDP letter grades (A to D-)

**How to access:**
1. Register free at cdp.net
2. Request data access for research
3. Download company responses

**Advantages:**
- Actual emissions data (not just ratings)
- Covers major U.S. firms
- Can calculate your own metrics

---

## Recommended Strategy for This Research

### Option A: S&P Global + CDP (Best for free data)
1. Get current ESG scores from S&P Global (manual collection for S&P 500)
2. Get historical emissions from CDP
3. Construct panel: ESG score changes vs emissions changes vs AI adoption

### Option B: Academic Data Access
1. Check if Florida Tech has WRDS access (includes MSCI ESG, Refinitiv ESG)
2. If yes, download full panel data with historical scores
3. Much easier for diff-in-diff analysis

### Option C: Proxy Using Emissions Intensity
1. Use EPA GHGRP for emissions (actual data, not ratings)
2. Calculate emissions/revenue as your own "E proxy"
3. More objective than ESG ratings (which have rater disagreement issues)

---

## ESG Score Variables to Collect

| Variable | Description | Source |
|----------|-------------|--------|
| `esg_score` | Overall ESG composite | S&P Global, MSCI |
| `e_score` | Environmental pillar | S&P Global, MSCI |
| `s_score` | Social pillar | S&P Global, MSCI |
| `g_score` | Governance pillar | S&P Global, MSCI |
| `carbon_intensity` | CO2/revenue | CDP, EPA GHGRP |
| `scope1_emissions` | Direct emissions | CDP |
| `scope2_emissions` | Electricity emissions | CDP |
| `climate_target` | Has net-zero target | CDP |

---

## Sample Python for S&P Global Scraping

```python
# Note: Respect rate limits and terms of service
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_sp_esg(ticker):
    """Get ESG score from S&P Global search"""
    # This is a placeholder - actual implementation would need
    # to handle their search interface
    pass

# Alternative: Use their downloadable reports
# Many companies publish their S&P Global ESG scores in sustainability reports
```

---

## Key Insight for Your Research

The **disagreement between ESG raters** is actually relevant to your hypothesis:

- Firms adopting AI may see DIVERGENT ESG signals
- Some raters may penalize energy use (E goes down)
- Others may reward efficiency/innovation (E stays same)
- This creates natural variation to exploit

Consider measuring:
1. Level of ESG score
2. Change in ESG score pre/post AI adoption
3. Dispersion across raters (if multiple sources available)

---

*Last updated: February 2026*
