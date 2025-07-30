"""
Fetch 90‑day Lis Pendens from ACRIS – Real Property Master (view cemy-trp6).
"""

import os
import requests
import datetime as dt
import pandas as pd

def run() -> pd.DataFrame:
    token = os.getenv("NYC_APP_TOKEN")
    if not token:
        raise RuntimeError("NYC_APP_TOKEN is missing")

    since = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00")
    API    = "https://data.cityofnewyork.us/resource/cemy-trp6.json"
    params = {
        "$select":      "borough,block,lot,recorded_date",
        "$where":       f"doc_type='LP' AND recorded_date >= '{since}'",
        "$limit":       50000,
        "$$app_token":  token
    }

    # Fire the request
    resp = requests.get(API, params=params, timeout=30)
    resp.raise_for_status()

    df = pd.DataFrame(resp.json())
    if df.empty:
        return pd.DataFrame(columns=["bbl", "lp_date"])

    # Build a zero‑padded 10‑digit BBL
    df["bbl"] = (
        df["borough"].astype(str).str.zfill(1) +
        df["block"].astype(str).str.zfill(5)   +
        df["lot"].astype(str).str.zfill(4)
    )
    df["lp_date"] = pd.to_datetime(df["recorded_date"]).dt.date

    return df[["bbl", "lp_date"]]







