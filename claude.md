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
| **CDP Open Data Portal** | Corporate climate disclosures: emissions (Scope 1, 2, 3), water consumption, climate strategy | cdp.net (free registration) |
| **EPA GHGRP** | Facility-level emissions for all large U.S. emitters | ghgdata.epa.gov (FLIGHT tool) |
| **EPA eGRID** | Regional electricity grid emission factors | epa.gov/egrid |
| **Corporate sustainability reports** | Detailed environmental data from Google, Microsoft, Meta, Amazon, Apple | Company websites |
| **Yahoo Finance ESG** | Sustainalytics risk ratings displayed publicly | finance.yahoo.com (scrapeable) |
| **S&P Global ESG Scores** | Some scores freely available | spglobal.com (free registration) |

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

## Proposed Empirical Design (Free Data Only)

### Step 1: AI Adoption Intensity
Construct from 10-K keyword counts (SEC EDGAR) for S&P 500 or Russell 3000 firms, 2018–2025

### Step 2: Environmental Performance
Measure using CDP emissions data or EPA GHGRP facility-level emissions matched to parent firms

### Step 3: Identification Strategy
Use ChatGPT launch (November 2022) as a shock, interacted with industry-level AI exposure from Felten et al. scores. Industries with high task exposure to AI faced stronger competitive pressure to adopt.

### Step 4: Track Outcomes
Post-shock changes in:
- Emissions intensity (from CDP/EPA)
- ESG scores (scraped from Yahoo Finance/S&P Global)
- High- vs. low-exposure firms comparison

### Step 5: Financial Outcomes
From Yahoo Finance: stock returns, market cap changes, Tobin's Q approximations

### Step 6: Heterogeneity Analysis
- ESG investor concentration (from 13F filings)
- Regional grid carbon intensity (from EPA eGRID)

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

### Requires Manual Download

| Dataset | Instructions | Why |
|---------|--------------|-----|
| **PatentsView** | See `data/patents/DOWNLOAD_INSTRUCTIONS.txt` | Files >10GB, need AI CPC codes |
| **CDP 2018-2023** | Register at cdp.net/en/data | Need Scope 2 for post-ChatGPT analysis |
| **ESG Scores** | Yahoo Finance API deprecated; use S&P Global free tier | API restrictions |

### Scripts Available (in `scripts/` folder)

| Script | Purpose | Usage |
|--------|---------|-------|
| `download_data.py` | Main download orchestrator | `python3 scripts/download_data.py` |
| `sec_edgar_scraper.py` | Extract AI keywords from 10-K filings | `python3 scripts/sec_edgar_scraper.py` |
| `yahoo_esg_scraper.py` | ESG score collection (currently restricted) | `python3 scripts/yahoo_esg_scraper.py` |
| `process_ghgrp_all_years.py` | Process EPA GHGRP 2010-2023, match to S&P 500 | `python3 scripts/process_ghgrp_all_years.py` |
| `build_ai_exposure_index.py` | Build AI exposure index from O*NET data | `python3 scripts/build_ai_exposure_index.py` |
| `process_cdp_scope2.py` | Process CDP Scope 2 data, merge with GHGRP | `python3 scripts/process_cdp_scope2.py` |

### Analysis Scripts (in `analysis/` folder)

| Script | Purpose | Output |
|--------|---------|--------|
| `01_emissions_analysis.py` | Descriptive stats, emissions trends by sector | Figures 1-4, yearly summaries |
| `02_diff_in_diff_analysis.py` | DiD regression: AI exposure × Post-ChatGPT | Figures 5-6, regression tables |
| `03_scope2_analysis.py` | Scope 2 importance, Big Tech emissions | Figures 7-8, measurement gap analysis |

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

---

## New Analysis Strategies (February 2026)

### Strategy 1: ESG Score Decomposition (E, S, G Pillars)
- **Status:** Framework ready, needs commercial ESG data
- **Prediction:** "Scissors" pattern - E pillar deteriorates, S/G improve
- **Data needed:** MSCI or Sustainalytics pillar scores

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
- [x] **Strategy 2:** Utility electricity DiD (hub vs control states) - 9.1% effect, p=0.007
- [x] **Strategy 3:** Investor pricing analysis - 0.95 correlation
- [x] **Strategy 4:** Builder/user classification - 27 builders, 205 users
- [ ] **Strategy 1:** Obtain decomposed ESG scores (E, S, G separately)
- [ ] Download formal EIA Form 861 data for utility analysis
- [ ] Run full SEC EDGAR scraper on S&P 500 (`python3 scripts/sec_edgar_scraper.py`)
- [ ] Download PatentsView bulk files manually (see instructions)

---

*Last updated: February 2026*
