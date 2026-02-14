# AI Adoption and ESG Trade-offs: Research Notes

## Research Premise

**Core question:** Does AI adoption create a productivity-ESG trade-off for public firms?

**The tension:** Firms that aggressively utilize AI (and by extension, data centers with massive energy footprints) may boost output and competitiveness but take a hit on their environmental/social governance scores — which increasingly matter for institutional investors, index inclusion, and cost of capital. Meanwhile, firms that hold back preserve ESG ratings but risk falling behind competitively.

---

## Key Dimensions to Develop

### Identification Strategy
- Exogenous variation in AI adoption pressure across industries or firms
- Differential exposure to large language model capabilities by industry (some sectors had more "automatable" tasks pre-ChatGPT)
- Supply-side shocks to data center capacity (e.g., regional energy grid constraints)
- Regulatory variation in ESG reporting requirements across states or countries

### Measurability
- ESG scores from providers like MSCI, Sustainalytics, or Bloomberg have known issues with disagreement across raters
- Decompose ESG into E, S, and G separately — the energy/carbon channel primarily hits the E pillar
- S and G components might actually improve with AI adoption (better compliance monitoring, governance tools), creating interesting heterogeneity

### Financial Channel
- Test whether the ESG penalty from AI adoption actually affects firm value or cost of capital
- Test whether investors are "forgiving" the ESG hit because they recognize the productivity gains
- Gets at whether ESG scores are being priced efficiently in the context of technological disruption

### Data Possibilities
- Firm-level AI adoption measures: patent filings in AI, job postings for AI roles, earnings call mentions of AI
- ESG score changes and financial performance (Tobin's Q, ROA, stock returns)
- Staggered timing of AI adoption across firms could support a diff-in-diff or event study framework

### Policy Angle
- Should ESG frameworks account for the purpose of energy consumption?
- A data center powering productivity-enhancing AI is different from inefficient fossil fuel use
- Current ESG metrics may not distinguish them

---

## Literature Landscape

### 1. AI Adoption → ESG Improvement (Dominant Finding)

The overwhelming majority of recent work finds that AI adoption improves ESG scores. This is almost entirely based on Chinese A-share listed firms using panel fixed effects.

**Proposed mechanisms:**
- Better internal controls
- Financing constraint alleviation
- Green innovation
- Supply chain efficiency

**Key papers:**
- 2025 study using 22,000+ Chinese firm-year observations showing AI boosts all three ESG pillars, with effects strongest in large firms and non-polluting industries
- AI enhances ESG through financing constraints, external oversight, and information disclosure channels
- Rapid literature review confirms predominantly positive relationship between AI and firm-level ESG performance

### 2. Big Tech's Emissions Crisis (Empirical Reality)

Evidence that AI adoption is destroying the environmental component of ESG for firms building AI infrastructure:

- Alphabet's emissions rose nearly 50% since 2019
- Meta's location-based emissions more than doubled
- Microsoft's rose 23.4% since 2020 — all driven by data center electricity demand
- In 2025, Microsoft, Google, Amazon, and Meta projected to spend combined $320 billion on AI infrastructure
- Harvard study: carbon intensity of electricity used by data centers was 48% higher than U.S. average
- Growing shareholder resolutions on whether tech companies' climate commitments are achievable alongside AI expansion

### 3. AI and Productivity/Competition

- AI adoption associated with firm growth and increased employment but — crucially — not yet with measurable productivity gains
- Strong evidence of increased industry concentration
- Future TFP gains from AI estimated conservatively at 0.07 to 0.68 percentage points annually
- "Productivity paradox" where manufacturing firms see productivity losses before longer-term gains

### 4. Research Gap (Your Contribution)

**Existing literature:** AI as a tool that firms use to improve ESG reporting, monitoring, and compliance

**Your idea:** The equilibrium trade-off for firms that must decide whether to adopt AI knowing it comes with real environmental costs (energy, water, carbon from compute infrastructure), and whether financial markets price this tension

**Key differentiation:**
- Heterogeneity between firms that build AI infrastructure (E scores worsen) vs. firms that merely use AI services (ESG may improve)
- Cross-sectional variation in ESG investor sensitivity
- ChatGPT release (November 2022) as a shock to competitive pressure to adopt AI

---

## Freely Available Data Sources

### AI Adoption Measures

| Source | Description | Access |
|--------|-------------|--------|
| **PatentsView** | Complete USPTO patent data with assignee-firm matching; filter by AI-related CPC codes | patentsview.org |
| **SEC EDGAR** | 10-K and 10-Q full-text filings; count AI-related keywords (artificial intelligence, machine learning, deep learning, neural network, generative AI) | sec.gov/edgar |
| **Google Trends** | Industry-level search interest in AI terms | trends.google.com |
| **O*NET Online** | Task-level occupation descriptions; combine with BLS industry-occupation matrices for AI exposure scores | onetonline.org |
| **Felten et al. AI Exposure Indices** | Pre-computed AI occupational exposure scores | GitHub/replication files |

### ESG Data

| Source | Description | Access |
|--------|-------------|--------|
| **Kaggle S&P 500 ESG** | Sustainalytics ESG risk ratings for 430 S&P 500 firms | kaggle.com (downloaded ✓) |
| **CDP Open Data Portal** | Corporate climate disclosures: emissions (Scope 1, 2, 3), water consumption, climate strategy | cdp.net (free registration) |
| **EPA GHGRP** | Facility-level emissions for all large U.S. emitters | ghgdata.epa.gov (FLIGHT tool) |
| **EPA eGRID** | Regional electricity grid emission factors | epa.gov/egrid |
| **Corporate sustainability reports** | Detailed environmental data from Google, Microsoft, Meta, Amazon, Apple | Company websites |
| **Yahoo Finance ESG** | ~~Sustainalytics risk ratings~~ **DEPRECATED** (API returns 404) | ~~finance.yahoo.com~~ |
| **MSCI ESG Search** | Free lookup tool with rating history | msci.com (anti-bot protection) |

### Financial Data

| Source | Description | Access |
|--------|-------------|--------|
| **SEC EDGAR** | All public filings including financials | sec.gov/edgar |
| **FRED** | Macroeconomic controls | fred.stlouisfed.org |
| **Yahoo Finance / yfinance** | Stock prices, market cap, basic financial ratios | Python library |
| **Macrotrends.net** | Historical financial statements (10+ years) | macrotrends.net |
| **SEC 13F filings** | Institutional holdings data | sec.gov/edgar |
| **Ken French Data Library** | Factor returns and industry portfolio data | Dartmouth website |

---

## Downloaded Data Status

### Successfully Downloaded (in `data/` folder)

| Dataset | File | Size | Description |
|---------|------|------|-------------|
| **EPA eGRID** | `epa_egrid/eGRID2022_data.xlsx` | 15 MB | Regional electricity grid emission factors |
| **EPA GHGRP Raw** | `epa_ghgrp/raw/2023 Data Summary Spreadsheets/ghgp_data_*.xlsx` | 30 MB | Facility-level emissions 2010-2023 (14 years) |
| **EPA GHGRP Parent** | `epa_ghgrp/raw/EPA Parent Company Data.xlsb` | 8 MB | Parent company ownership data |
| **EPA GHGRP Panel** | `epa_ghgrp/processed/ghgrp_company_year_sp500_all_years.csv` | 44 KB | 121 S&P 500 firms × 14 years (1,636 company-year obs) |
| **EPA GHGRP Facilities Panel** | `epa_ghgrp/processed/ghgrp_facilities_sp500_all_years.csv` | 3 MB | 23,439 facility-year observations for S&P 500 |
| **EPA GHGRP 2023 Only** | `epa_ghgrp/processed/ghgrp_company_year_sp500.csv` | 3 KB | 116 S&P 500 firms (2023 snapshot) |
| **Kaggle ESG** | `kaggle_esg/SP 500 ESG Risk Ratings.csv` | 800 KB | **430 S&P 500 firms with Sustainalytics E/S/G scores** |
| **Big Tech ESG Panel** | `esg_scores/big_tech_esg_manual.csv` | 2 KB | **6 companies × 5 years (2019-2023) MSCI ratings** |
| **Fortune Most Admired** | `esg_scores/fortune_most_admired.csv` | 1 KB | Top 10 most admired companies (2024) |
| **Newsweek Responsible** | `esg_scores/newsweek_responsible.csv` | 3 KB | Top 49 most responsible companies (2024) |
| **Multi-source Summary** | `esg_scores/esg_sources_summary.csv` | 2 KB | Consolidated Big Tech ESG across sources |
| **CDP Emissions** | `cdp/*.csv` | 2 MB | Corporate emissions 2010-2013 (Scope 1 + 2) |
| **CDP Processed** | `analysis/output/cdp_emissions_sp500.csv` | 40 KB | 183 S&P 500 firms with Scope 1 & 2 (2011-2013) |
| **Ken French Factors** | `ken_french/F-F_Research_Data_Factors_daily.csv` | 1.1 MB | Daily Fama-French factor returns |
| **Ken French Industries** | `ken_french/48_Industry_Portfolios_Daily.csv` | 20 MB | 48 industry portfolio returns |
| **FRED Macro Data** | `fred/*.csv` | 58 KB | GDP, unemployment, CPI, Fed funds, S&P 500, industrial production |
| **S&P 500 List** | `sp500_constituents.csv` | 52 KB | 503 companies with tickers, sectors, CIK |
| **Stock Data** | `stocks/*.csv` | 2.2 MB | Price history & info for 8 major tech firms (2018-2025) |
| **O*NET Data** | `ai_exposure/onet_*.txt` | 16 MB | Abilities, work activities, occupations for AI exposure calculation |
| **SEC Tickers** | `sec_filings/company_tickers.json` | 1.9 KB | Ticker-to-CIK mapping |
| **Test AI Keywords** | `sec_filings/test_ai_keywords.csv` | 1.4 KB | Sample 10-K AI keyword extraction (GOOGL, XOM, WMT) |

### ESG Data Availability Summary

| Source | Status | Data Type | Coverage |
|--------|--------|-----------|----------|
| **Kaggle Sustainalytics** | ✅ Downloaded | Cross-sectional | 503 firms, June 2024 |
| **Manual Big Tech Panel** | ✅ Created | Time series | 6 firms, 2019-2023 |
| **Fortune Most Admired** | ✅ Scraped | Ranking | Top 10 companies |
| **Newsweek Most Responsible** | ✅ Scraped | Ranking + Score | Top 49 companies |
| **Multi-source Summary** | ✅ Created | Consolidated | Big Tech + sectors |
| MSCI Scraper | ❌ Blocked | — | Anti-bot protection |
| Yahoo Finance API | ❌ Discontinued | — | 404 errors |
| yesg Package | ❌ Blocked | — | 429 rate limits |

### Requires Manual Download

| Dataset | Instructions | Why |
|---------|--------------|-----|
| **PatentsView** | See `data/patents/DOWNLOAD_INSTRUCTIONS.txt` | Files >10GB, need AI CPC codes |
| **CDP 2018-2023** | Register at cdp.net/en/data | Need Scope 2 for post-ChatGPT analysis |

---

## Scripts Available

### Data Collection Scripts (in `scripts/` folder)

| Script | Purpose | Usage |
|--------|---------|-------|
| `download_data.py` | Main download orchestrator | `python3 scripts/download_data.py` |
| `sec_edgar_scraper.py` | Extract AI keywords from 10-K filings | `python3 scripts/sec_edgar_scraper.py` |
| `yahoo_esg_scraper.py` | ESG score collection (currently restricted) | `python3 scripts/yahoo_esg_scraper.py` |
| `process_ghgrp_all_years.py` | Process EPA GHGRP 2010-2023, match to S&P 500 | `python3 scripts/process_ghgrp_all_years.py` |
| `build_ai_exposure_index.py` | Build AI exposure index from O*NET data | `python3 scripts/build_ai_exposure_index.py` |
| `process_cdp_scope2.py` | Process CDP Scope 2 data, merge with GHGRP | `python3 scripts/process_cdp_scope2.py` |
| `scrape_msci_esg.py` | MSCI ESG scraper (py-msci-esg wrapper) | Blocked by MSCI |
| `scrape_msci_esg_custom.py` | Custom Selenium MSCI scraper | Blocked by anti-bot |
| `fetch_esg_data.py` | Multi-source ESG collector + Big Tech panel | `python3 scripts/fetch_esg_data.py` |
| `scrape_just_capital.py` | Just Capital rankings scraper | `python3 scripts/scrape_just_capital.py` |
| `scrape_esg_sources.py` | Multi-source ESG scraper (Fortune, Newsweek) | `python3 scripts/scrape_esg_sources.py` |

### Analysis Scripts (in `analysis/` folder)

| Script | Purpose | Output |
|--------|---------|--------|
| `01_emissions_analysis.py` | Descriptive stats, emissions trends by sector | Figures 1-4, yearly summaries |
| `02_diff_in_diff_analysis.py` | DiD regression: AI exposure × Post-ChatGPT | Figures 5-6, regression tables |
| `03_scope2_analysis.py` | Scope 2 importance, Big Tech emissions | Figures 7-8, measurement gap analysis |
| `04_new_strategies.py` | Builder/user decomposition, investor pricing | Figures 9-10 |
| `05_utility_electricity_analysis.py` | Utility-level DiD for data center hubs | Figures 11-12, hub vs control |
| `06_big_tech_deep_dive.py` | Big Tech Scope 2 panel (2019-2023) | Figure 13, Tables 2-4 |
| `07_esg_trajectory_analysis.py` | ESG rating trajectories over time | Figures 14-15 |
| `08_kaggle_esg_analysis.py` | Sustainalytics ESG cross-sectional analysis | Figures 16-18 |
| `09_multi_source_esg_analysis.py` | Multi-source ESG comparison (Fortune, Newsweek, Sustainalytics) | Figure 19 |

---

## Preliminary Findings

### Diff-in-Diff Results (GHGRP Scope 1)

**Treatment:** High AI Exposure × Post-ChatGPT (Nov 2022)

| Model | Coefficient | SE | P-value |
|-------|-------------|-----|---------|
| Basic DiD | +0.057 | 0.425 | 0.893 |
| Firm FE | +0.006 | 0.062 | 0.921 |
| Continuous AI | -0.020 | 0.031 | 0.519 |

**Result:** No significant differential effect — but this is likely a **measurement artifact**.

### Critical Data Limitation

GHGRP only captures **Scope 1** (direct combustion). Tech/AI emissions are **Scope 2** (purchased electricity):

| Company | Scope 1 | Scope 2 | % Missing from GHGRP |
|---------|---------|---------|---------------------|
| Microsoft | 0.13M | 7.10M | 98% |
| Alphabet | 0.08M | 7.48M | 99% |
| Meta | 0.05M | 3.81M | 99% |
| Amazon | 9.12M | 10.20M | 53% |

**Big Tech emissions grew 60-176% from 2020-2023** — none of this shows up in GHGRP.

### AI Exposure Index (O*NET-based)

| Sector | AI Exposure Score |
|--------|-------------------|
| Information Technology | 81.5 |
| Financials | 81.2 |
| Health Care | 65.1 |
| Consumer Discretionary | 62.6 |
| Utilities | 42.0 |
| Materials | 37.2 |

### Big Tech ESG Trajectory (2019-2023)

| Company | MSCI 2019 | MSCI 2023 | Change | Sustainalytics Risk |
|---------|-----------|-----------|--------|---------------------|
| Microsoft | AAA | AAA | 0 | 15.1 (Low) |
| Alphabet | A | BB | -3 | 24.2 (Medium) |
| Meta | B | CCC | -2 | 34.1 (High) |
| Amazon | BBB | BB | -1 | 30.6 (High) |
| Apple | A | AA | +1 | 17.2 (Low) |
| NVIDIA | BBB | AA | +2 | 13.6 (Low) |

**Key insight:** Alphabet, Meta, Amazon show ESG deterioration; Microsoft maintains AAA through carbon offsets; NVIDIA improves (sells chips, doesn't own data centers).

### Multi-Source ESG Comparison (2024)

| Company | Fortune Rank | Newsweek Rank | NW Score | Sust. Risk | MSCI |
|---------|--------------|---------------|----------|------------|------|
| Apple | 1 | - | - | 17.2 | AA |
| Microsoft | 2 | 34 | 87.3 | 15.1 | AAA |
| Amazon | 3 | - | - | 30.6 | BB |
| NVIDIA | 4 | 25 | 84.8 | 13.6 | AA |
| Alphabet | 8 | - | - | 24.2 | BB |
| Meta | - | - | - | 34.1 | CCC |

**Key insight:** Apple, Amazon, Alphabet, and Meta are absent from Newsweek's "Most Responsible" top 49, despite high Fortune admiration rankings. This supports the hypothesis that corporate reputation ≠ ESG performance for AI infrastructure builders.

---

## Completed Analysis Strategies

### Strategy 1: ESG Score Decomposition (E, S, G Pillars)
- **Status:** COMPLETED ✓
- **Data:** Kaggle Sustainalytics (430 firms) + Manual Big Tech panel (2019-2023)
- **Findings:**
  - META and AMZN rated "High Risk" (34.1, 30.6)
  - MSFT, AAPL, NVDA rated "Low Risk" (15.1, 17.2, 13.6)
  - Technology sector has 2nd-lowest ESG risk despite high AI exposure (paradox)
  - Social pillar drives most Big Tech differentiation (not Environmental)
  - Negative correlation between AI exposure and ESG risk at sector level

### Strategy 2: Utility Electricity Demand (Data Center Hubs)
- **Status:** COMPLETED ✓
- **Result:** Hub states saw **9.1% more electricity demand growth** post-ChatGPT (p=0.007)
- Hub states: VA, TX, OR, AZ, GA
- Control states: MT, WY, VT, ME
- Hub growth 2022-2024: 64.9% vs Control: 48.0% (16.8 pp differential)

### Strategy 3: Investor Pricing of the Trade-off
- **Status:** COMPLETED ✓
- **Result:** Correlation between emissions growth and stock returns = **0.947**
- Markets are "forgiving" environmental costs for AI productivity
- META: +174% emissions → +502% stock return
- NVDA: +1,114% stock return (AI chips)

### Strategy 4: Builder vs. User Decomposition
- **Status:** COMPLETED ✓
- AI Infrastructure Builders: 27 firms (MSFT, GOOGL, AMZN, META, NVDA, etc.)
- AI Users (high-exposure non-builders): 205 firms
- Builders have minimal Scope 1 in GHGRP (their footprint is Scope 2)
- Users may see ESG improvement from AI-enhanced operations

---

## Paper Status

**File:** `paper/ai_esg_tradeoff.tex`
**Current version:** 23 pages, 9 figures, 6 tables

### Sections:
1. Introduction
2. Related Literature (AI/ESG, Big Tech emissions, Scope measurement)
3. Data (EPA GHGRP, AI Exposure Index, CDP, Sustainalytics)
4. Empirical Strategy (DiD identification, parallel trends)
5. Results (DiD estimates, event study, Big Tech deep dive)
6. Alternative Strategies (utility electricity, builder/user, investor pricing)
7. Discussion (ESG measurement, AI exposure mismatch, scissors pattern, Sustainalytics validation, research agenda)
8. Conclusion

### Key Tables:
1. DiD Estimates: AI Exposure and Emissions
2. Big Tech Scope 2 Location-Based Emissions (2019-2023)
3. GHGRP vs. Sustainability Reports: 2023 Comparison
4. Location-Based vs. Market-Based Scope 2
5. DiD Estimates: Data Center Hub States vs. Control States
6. Big Tech ESG Risk Scores (Sustainalytics)

### Key Figures:
1. Parallel Trends and Event Study
2. Big Tech Emissions Deep Dive
3. Major Data Center Hub States
4. Utility Electricity Demand Analysis
5. Builder vs. User Analysis
6. ESG Pillar Scissors Pattern
7. ESG Risk by Sector and AI Exposure
8. Big Tech ESG Risk Decomposition

---

## Next Steps

- [x] Download EPA eGRID regional emission factors
- [x] Set up SEC EDGAR scraping for 10-K AI keyword counts
- [x] Download Ken French factor data
- [x] Download S&P 500 constituent list
- [x] Download O*NET data for AI exposure calculation
- [x] Download EPA GHGRP from Envirofacts (2010-2023 facility data, parent company matching)
- [x] Match EPA GHGRP facilities to S&P 500 companies (121 firms, 2,175 facilities)
- [x] Process GHGRP panel data for all years (1,636 company-year observations, 109 firms with complete 14-year panel)
- [x] Construct AI exposure index from O*NET data (873 occupations, 11 GICS sectors)
- [x] Run diff-in-diff analysis with firm fixed effects
- [x] Process CDP Scope 2 data (2011-2013)
- [x] Document Scope 2 measurement gap for Big Tech
- [x] **Strategy 1:** ESG pillar decomposition with Sustainalytics data
- [x] **Strategy 2:** Utility electricity DiD (hub vs control states) - 9.1% effect, p=0.007
- [x] **Strategy 3:** Investor pricing analysis - 0.95 correlation
- [x] **Strategy 4:** Builder/user classification - 27 builders, 205 users
- [x] Download Kaggle S&P 500 ESG dataset (430 firms)
- [x] Create Big Tech ESG trajectory panel (2019-2023)
- [x] Add Sustainalytics validation to paper
- [x] Scrape Fortune Most Admired rankings (Top 10)
- [x] Scrape Newsweek Most Responsible rankings (Top 49 with scores)
- [x] Create multi-source ESG comparison analysis
- [ ] Download formal EIA Form 861 data for utility analysis
- [ ] Run full SEC EDGAR scraper on S&P 500 (`python3 scripts/sec_edgar_scraper.py`)
- [ ] Download PatentsView bulk files manually (see instructions)
- [ ] Obtain CDP data for 2018-2023 (need registration)

---

## Git Repository

**Remote:** github.com:alina-malkova/esg.git
**Branch:** main

### Recent Commits:
- `7e6dcb2` Add Sustainalytics ESG validation to paper
- `391b2fe` Add Kaggle S&P 500 ESG Risk Ratings analysis
- `a27a603` Add ESG trajectory analysis and MSCI scraping infrastructure
- `bdf1b0c` Add Big Tech deep dive analysis and strengthen paper
- `3fb4fd4` Add new analysis strategies: utility electricity DiD, investor pricing, builder/user decomposition

---

*Last updated: February 13, 2026*
