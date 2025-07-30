"""
Headless Playwright scraper for Nassau Lis Pendens.
"""

import os, csv, datetime as dt, pandas as pd
from playwright.sync_api import sync_playwright

DOC_CODES = ["LIS PENDENS", "LPX10", "LPX22", "LPX23", "LPX24"]

def run():
    user = os.getenv("NASSAU_USER")
    pw   = os.getenv("NASSAU_PASS")
    if not user or not pw:
        raise RuntimeError("Missing NASSAU_USER/PASS secrets")

    rows = []
    six_months = (dt.date.today() - dt.timedelta(days=183)).strftime("%m/%d/%Y")
    today      = dt.date.today().strftime("%m/%d/%Y")

    with sync_playwright() as p:
        br = p.chromium.launch(headless=True)
        pg = br.new_page()
        pg.goto("https://i2p.uslandrecords.com/NY/Nassau/D/Default.aspx")

        pg.fill("#username", user)
        pg.fill("#password", pw)
        pg.click("text=Login")

        pg.hover("text=Search Criteria")
        pg.click("text=Recorded Date Search")

        for code in DOC_CODES:
            pg.select_option("select[name='documentType']", label=code)

        pg.fill("input[name='fromDate']", six_months)
        pg.fill("input[name='toDate']", today)
        pg.click("input[value='Search']")

        # 100 rows per page
        pg.click("text=100")

        def scrape_page():
            for tr in pg.query_selector_all("table#results tr.dataRow"):
                tds = [td.inner_text().strip() for td in tr.query_selector_all("td")]
                # columns: Doc#, File Date, Type Desc., #pgs, Book, Vol, Page …
                rows.append({
                    "s": tds[4][:3].lstrip("0"),
                    "b": tds[4][3:8].lstrip("0"),
                    "l": tds[4][8:].lstrip("0"),
                    "record_dt": tds[1],
                    "doc_type": tds[2],
                })

        scrape_page()
        while pg.query_selector("a:text('Next')"):
            pg.click("a:text('Next')")
            scrape_page()

        br.close()

    df = pd.DataFrame(rows)
    df["sbl"] = df["s"] + "-" + df["b"] + "-" + df["l"]
    df["lp_flag"] = 1
    return df[["sbl", "record_dt", "lp_flag"]]
