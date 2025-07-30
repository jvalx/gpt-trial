"""
Fetch Lis Pendens (last 90 days) from NYC ACRIS Real‑Property‑Master API.
Build BBL, keep only rows whose doc_type contains 'LIS'.
"""

import os, requests, datetime as dt, pandas as pd, urllib.parse as up

API = "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"

def run() -> pd.DataFrame:
    token = os.getenv("NYC_APP_TOKEN")
    if not token or len(token) < 20:
        raise RuntimeError("NYC_APP_TOKEN env‑var missing or too short")

    since = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00")

    params = {
        "$select": "document_date,doc_type,recorded_borough,block,lot",
        "$where":  f"document_date >= '{since}'",
        "$limit":  50000,
        "$$app_token": token,
    }

    # Debug: show query without token
    dbg = {k: v for k, v in params.items() if k != "$$app_token"}
    print("ACRIS URL:", API + "?" + up.urlencode(dbg, safe=":,>= '"))

    r = requests.get(API, params=params, timeout=30)
    r.raise_for_status()

    df = pd.DataFrame(r.json())
    if df.empty:
        print("Acris LP: 0 rows (last 90 days)")
        return pd.DataFrame(columns=["bbl", "lp_date"])

    # Keep only Lis Pendens rows
    df = df[df["doc_type"].str.contains("LIS", case=False, na=False)]

    # Build zero‑padded BBL
    df["bbl"] = (
        df["recorded_borough"].astype(str).str.zfill(1) +
        df["block"].astype(str).str.zfill(5) +
        df["lot"].astype(str).str.zfill(4)
    )

    # Convert date
    df["lp_date"] = pd.to_datetime(df["document_date"]).dt.date

    print(f"Acris LP rows kept: {len(df)}")
    return df[["bbl", "lp_date"]]






