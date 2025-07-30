"""
Fetch Lis Pendens (last 90 days) from ACRIS Document Master (ID 9bhx‑743a).
"""

import os, requests, datetime as dt, pandas as pd, urllib.parse as up

API = "https://data.cityofnewyork.us/resource/9bhx-743a.json"

def run() -> pd.DataFrame:
    token = os.getenv("NYC_APP_TOKEN")
    if not token or len(token) < 20:
        raise RuntimeError("NYC_APP_TOKEN env‑var missing or wrong")

    since = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00")

    params = {
        "$select": "borough,block,lot,recorded_date",
        "$where":  f"doc_type='LP' AND recorded_date >= '{since}'",
        "$limit":  50000,
        "$$app_token": token,
    }

    dbg = {k:v for k,v in params.items() if k != "$$app_token"}
    print("ACRIS URL:", API + "?" + up.urlencode(dbg, safe=":,>= '"))

    r = requests.get(API, params=params, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    if df.empty:
        print("Acris LP: 0 rows (last 90 days)")
        return pd.DataFrame(columns=["bbl", "lp_date"])

    df["bbl"] = (
        df["borough"].astype(str).str.zfill(1) +
        df["block"].astype(str).str.zfill(5)   +
        df["lot"].astype(str).str.zfill(4)
    )
    df["lp_date"] = pd.to_datetime(df["recorded_date"]).dt.date
    print(f"Acris LP rows kept: {len(df)}")
    return df[["bbl", "lp_date"]]






