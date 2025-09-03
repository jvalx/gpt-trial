# Distressed-Seller Radar

Identifies NYC properties showing signs of distress (recent lis pendens filings, tax liens, severe housing violations, or vacate orders). It also includes Nassau County lis pendens data via a scraper. The pipeline runs weekly (every Monday) to produce a top-100 ranked list of properties with a “distress score.” This helps analysts quickly spot properties that may be motivated sellers due to financial or safety issues.

Features
- Multi-Source Data Fetching: Retrieves data from NYC Open Data APIs (ACRIS, DOF Liens, HPD Violations/Vacate) and Nassau County’s records site
- Automated Scoring: Merges datasets by Building Block Lot (BBL) and computes a simple distress score (Lis Pendens = 2 points; Liens, Violations, Vacate = 1 point each)
- Top 100 Ranking: Filters and sorts results by score (and recency of lis pendens) to output the 100 most distressed properties of the week
- Optional Address Enrichment: Attempts to append owner mailing address info from the Property Address Directory (PAD) dataset (enrichment currently requires code fix – see Known Issues).
- CI/CD Integration: Runs on a schedule via GitHub Actions, saving outputs for download. Also runnable locally for ad-hoc analysis.

Architecture
The pipeline consists of five data fetchers feeding into a merge-and-rank step:
 NYC ACRIS (90-day Lis Pendens) --.
 NYC DOF Liens (tax liens list) ---+--> [Merge & Score] --> top100.csv + top100_enriched.csv
 NYC HPD Violations (Open C) ----'         (outputs in /outputs folder)
 NYC HPD Vacate Orders ---------'
 Nassau Lis Pendens Scraper ----'
Each fetcher returns a Pandas DataFrame, keyed by BBL (or SBL for Nassau). The main script orchestrates fetches in sequence and handles any failures (skipping a source on error)

Setup and Installation
1. Clone the repo (or copy the /etl folder into your project):
git clone https://github.com/jvalx/gpt-trial.git
cd gpt-trial

2. Install Python 3.11+ and create a virtual environment:
python3.11 -m venv .venv && source .venv/bin/activate

3. Install requirements:
pip install -r requirements.txt


Note: On first run, install the headless browser:
playwright install chromium


4.  Configure Environment Variables: Create a .env file or export in your shell:
NYC_APP_TOKEN – NYC OpenData app token. Required for ACRIS data (and improves rate limits for others). Obtain from data.cityofnewyork.us.
NASSAU_USER / NASSAU_PASS – Credentials for Nassau County’s land records portal. Required to include Nassau Lis Pendens; if unset, that step will be skipped
(No database needed) – All output is to CSV files.

5. Quickstart (Local Run):
# Activate virtual env as above, then:
export NYC_APP_TOKEN="your-token-here"
export NASSAU_USER="your-username"   # (optional, for Nassau)
export NASSAU_PASS="your-password"   # (optional)
python etl/main.py


This will run the pipeline end-to-end. On success, you’ll see Pipeline complete: YYYY-MM-DD in the console. Output CSVs will be in the outputs/ directory:
- top100.csv – core fields for top 100 properties.
- top100_enriched.csv – with owner address fields (if enrichment succeeded).


Usage
- Automated Weekly Run: The pipeline is set to run every Monday at 5:00am ET via GitHub Actions
  The action uses the same steps (install deps, playwright, run script) and uploads the outputs artifact for retrieval
- Ad-hoc Run: You can run it anytime locally as shown above. Ensure your environment variables are set each time.
- Development Mode: The scoring threshold is currently lenient (score >= 1) to include more results for inspection. In a production scenario, you might tighten this (e.g., >=3) to focus on more distressed cases.


Output Details
Each output CSV row represents a unique property (NYC BBL or Nassau S-B-L):
1. bbl – Borough-Block-Lot (10-digit NYC property identifier) or Nassau SBL (with dashes).
2. lp_date – Date of last lis pendens (foreclosure notice) if any in last 90 days.
3. total_due / cycle – Total amount due and cycle for any tax lien on the property (if multiple liens, values from source; typically one lien per property in list).
4. open_c_count – Number of open Class-C (immediately hazardous) HPD violations in the past year (only counted if ≥10 to flag worst cases).
5. vacate_flag – 1 if an active vacate order (building vacated by city order).
6. lien_flag, viol_flag – Boolean flags (1/0) indicating presence of any lien or >=10 class-C violations.
7. score – Distress score (0–5) = 2×(has recent LP) + 1×(has lien) + 1×(violations flag) + 1×(vacate flag). Higher means more indicators of distress.

The *_enriched.csv adds owner mailing address fields (house_number, street_name, owner_name, owner_address1, owner_city, owner_state, owner_zip) if the enrichment step succeeds. If that step fails or data is missing, those columns may be empty.

Troubleshooting
- Missing NYC_APP_TOKEN: If not provided, the ACRIS step will raise an error and be skipped. The pipeline will still run but ACRIS-dependent info (lis pendens) will be blank, and score may be lower for properties that actually have recent LPs. Always set a valid token if possible.
- Nassau Login Fails: If NASSAU_USER/PASS are wrong or not set, you’ll get a runtime error “Missing NASSAU_USER/PASS secrets” and the Nassau portion will be skipped. The rest of the pipeline still completes, but     Nassau SBLs won’t appear in outputs. Ensure your credentials are correct (the script may fail if the website UI changed – see Next Steps for maintaining the scraper).
- Playwright Issues: If the scraper crashes (e.g., due to a missing dependency or timeout), it will raise an exception and stop that step. Because this is inside the main try/except, the pipeline will catch it and   move on. Check that you installed Chromium via Playwright and that the environment can support headless browsing. Use DEBUG=pw:api (Playwright debug logs) for more info.
- Address Enrichment Failing: It’s known that the enrich_addresses step currently throws an error (name 'where' is not defined) and you’ll see a log line “❌ Address enrichment failed (NameError)…”. This is a bug (see Known Issues) – the pipeline will continue and still output the base top100.csv. You can ignore this error; it doesn’t stop the run.
- Data Discrepancies: The sources update at different frequencies (liens dataset might lag a few days, etc.). If a property expected to appear isn’t in top100, check raw source data or lower the score threshold.
- Output Empty: If top100.csv is empty, it could mean none of the sources returned data (unlikely), or all provided credentials were invalid. Run each fetch on its own to debug (they will throw exceptions on issues like HTTP 401 or network errors).

FAQ
Q: “What if I want to adjust the criteria or include more properties?”
A: You can tweak the score threshold in merge_score.py (line where it filters score >= 1). For example, using >=0 would include all properties with any flags, or >=3 (the intended production setting) would include only heavily distressed ones. You could also adjust the score formula (e.g., weight liens higher) directly in that file.
Q: “Can I integrate this with a database or dashboard?”
A: Yes. Currently, results are in CSV only. You could import merge_score.run() in another context to get a DataFrame and then load it into a database or use it in a web dashboard. Another approach is to modify main.py to save to a database (e.g., via SQLAlchemy) in addition to CSV. Ensure to parameterize credentials and avoid committing secrets.
Q: “How do I get an NYC OpenData token?”
A: Create a free account on data.cityofnewyork.us, then go to your profile’s App Tokens section to generate a new application token. Set it as NYC_APP_TOKEN. This raises your API limits (the pipeline requests up to 500k records for violations, which likely requires a token).
Q: “Why is address enrichment not working?”
A: There’s a known bug in the code where the query to the PAD dataset isn’t constructed properly (the variable where is undefined). This will be fixed soon (see Next Steps). In the meantime, you will have to manually look up addresses or fix the code as described in the Bug Log section below if you need that data.


# File-by-File Explainers

Below we explain each important file in the ETL module, including its role, how it works, and considerations for testing or improvement:

**etl/main.py – Pipeline Orchestrator.**
Defines `main()` which calls all fetchers in sequence, then calls `merge_score()` to combine results. It wraps each fetch call in a `try/except`: on error, it logs a warning and substitutes an empty DataFrame with the expected columns.
**Inputs:** no direct input (reads env vars internally).
**Outputs:** triggers creation of `outputs/top100.csv` and `outputs/top100_enriched.csv`.
**Key logic:** ensures that a failure in one data source won’t halt the pipeline.
**External deps:** relies on each fetcher and final merge.
**Risks:** if a fetcher raises unexpectedly (e.g., network timeout, JSON decode error), it will be caught here – but any unexpected error in `merge_score` (after the `try/except` blocks) would crash the pipeline (e.g., if writing CSV fails due to permission issues).
**Testing:** simulate errors (e.g., unset `NYC_APP_TOKEN` to cause a `RuntimeError` in the ACRIS fetch) to verify a warning is logged and the pipeline continues.

**etl/fetch\_acris\_lp.py – NYC ACRIS Lis Pendens Fetcher.**
Connects to NYC OpenData ACRIS (Real Property Master, resource `cemy-trp6`) to get lis pendens filings in the last 90 days. Requires `NYC_APP_TOKEN` and will raise `RuntimeError` if missing, since high-limit queries likely need a token. Selects borough/block/lot and `recorded_date`, filtering `doc_type='LP'` and date ≥ 90 days ago. Loads JSON to a DataFrame.
**Post-processing:** if no records, returns an empty DataFrame with columns `["bbl","lp_date"]`; otherwise constructs zero-padded 10-digit BBL (Borough+Block+Lot) and converts `recorded_date` to a date.
**Output:** DataFrame with BBL and `lp_date`.
**Failure modes:** HTTP errors or missing token raise exceptions (propagated to `main.py` handler).
**Dependencies:** `requests`, `pandas`.
**Test ideas:** mock `requests.get` to return a tiny JSON; verify BBL formatting and empty-branch columns.

**etl/fetch\_nyc\_liens.py – NYC Tax Liens Fetcher.**
Calls DOF tax liens dataset (`9rz4-mjek`) via GET (with `$select` for `borough, block, lot, total_due, lien_type, cycle`). Uses the app token via an HTTP header (if `NYC_APP_TOKEN` is not set, it sends no header; API may still respond with lower limits). Parses JSON to DataFrame.
**Post-processing:** concatenates borough+block+lot into 10-digit BBL (zero-padded) and sets constant `lien_flag = 1`.
**Returns:** `["bbl","total_due","cycle","lien_flag"]`.
**Risks:** portal downtime/non-JSON responses; large result truncation if limits exceeded.
**Tests:** mock a small JSON with one lien; verify BBL formatting (1-digit borough + 5 + 4 digits) and behavior without token.

**etl/fetch\_hpd\_violations.py – HPD Violations Fetcher.**
Queries HPD violations (`wvxf-dwi5`), filtering for **class C** and **Open** status in the last 365 days; selects `boro, block, lot, violationid` with a high row limit.
**Processing:** maps borough code **letter → digit** to form BBL via a dict. There’s likely a bug: `"B"` and `"K"` are both mapped to `"3"`; intended mapping is `"B"` (Bronx) → `"2"` and `"K"` (Brooklyn) → `"3"`. After forming BBL, groups by BBL and counts violations, then keeps only those with **≥10** open C violations, setting `viol_flag = 1`.
**Output:** `["bbl","open_c_count","viol_flag"]` (one row per qualifying BBL).
**Dependencies:** `requests`, token header recommended for stability.
**Tests:** lower threshold to 1 for testing; verify exclusion of buildings with <10 violations and correct Bronx mapping (BBL starts with “2”).

**etl/fetch\_hpd\_vacate.py – HPD Vacate Orders Fetcher.**
Fetches **active** vacate orders (no rescind date) from `tb8q-a3ar` using `$where actual_rescind_date IS NULL`. Selects just `bbl`, with a 50k limit. Appends `$$app_token` param when present (if empty, ideally handle similarly to others). Loads list of BBLs into a DataFrame.
**Post-processing:** adds `vacate_flag = 1`, returns `["bbl","vacate_flag"]`.
**Risks:** relies on timely rescind updates; potential truncation if dataset grows beyond limit.
**Tests:** dummy JSON with a couple BBLs; verify empty-result behavior returns the correct columns.

**etl/fetch\_nassau\_lp.py – Nassau Lis Pendens Scraper.**
Uses Playwright (headless Chromium) to log into Nassau County’s land records site and search for documents of types “LIS PENDENS” (codes LPX10, LPX22, etc.) recorded in the last \~6 months.
**Process:** fills login form with `NASSAU_USER/PASS`, navigates to recorded-date search, selects all LP codes, sets date range (\~183 days ago → today), runs search, sets results/page to 100, and scrapes the results table.
**Extraction:** parses Section/Block/Lot (SBL) from a column (first 3 chars = section, next 5 = block, remaining = lot), collects `record_dt` and `doc_type`, pages through results, compiles a DataFrame.
**Post-processing:** forms `sbl` as `Section-Block-Lot`, sets `lp_flag = 1`, returns `["sbl","record_dt","lp_flag"]`.
**Inputs:** requires valid Nassau credentials; otherwise raises `RuntimeError("Missing NASSAU_USER/PASS")` (caught by `main` as a skip).
**Risks:** highly dependent on site structure; needs Playwright browser/deps; can be slow; timeouts/element changes can break it.
**Tests:** hard to unit test without live site; can mock `playwright.sync_api.sync_playwright`; for live smoke test, reduce date window to 1 day to limit results.

**etl/merge\_score.py – Merge and Scoring Logic.**
Defines `run(acris, liens, viols, vacate, nassau)` to combine DataFrames and produce outputs, plus helper `enrich_addresses(df)` for address lookup.
**Merge:** builds a master list of unique BBLs across NYC datasets; left-joins each dataset’s fields onto this list (missing data → NaN).
**Score:** `2` points if `lp_date` present, plus `1` each for `lien_flag`, `viol_flag`, `vacate_flag`.
**Nassau merge:** if Nassau DF not empty, appends those entries (renaming `sbl`→`bbl`) with a fixed score of `2` (treated as LP-equivalent; they won’t have NYC flags).
**Filter & rank:** keep `score >= 1`, sort by score desc then `lp_date` desc, take top 100.
**Address enrichment:** attempts `enrich_addresses(df)` on top 100 to query PAD for owner address info. **Bug:** the `where` variable in the query is never defined, so this errors out. The exception is caught; an error is logged and the pipeline proceeds without enrichment.
**Outputs:** ensures `outputs/` exists; writes `top100.csv` and `top100_enriched.csv` (currently identical until the enrichment bug is fixed). Returns the enriched DataFrame (original top DF if enrichment failed).
**Risks:** assumes all BBL strings are 10-digit numeric; malformed BBLs could cause odd merges. If all sources are empty, CSVs may be empty (headers only) — pipeline should handle gracefully.
**Tests:** unit test score calculation with tiny fake DataFrames (e.g., all flags → score 5). Test Nassau rows appear with score 2 and `sbl`→`bbl` rename. After fixing enrichment, mock the PAD request and verify owner fields populate for known BBLs.


