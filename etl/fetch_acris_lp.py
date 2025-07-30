import os, requests, datetime as dt, pandas as pd

API   = "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"
TOKEN = os.getenv("NYC_APP_TOKEN")

def run():
    since = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00")

    params = {
        "$select": "bbl,document_date,document_type",
        "$where": f"document_date >= '{since}'",
        "$limit": 50000,
        "$$app_token": TOKEN,
    }
    r = requests.get(API, params=params)
    r.raise_for_status()

    df = pd.DataFrame(r.json())
    if df.empty:
        return pd.DataFrame(columns=["bbl", "lp_date"])

    # keep only Lis Pendens rows (any variant)
    df = df[df["document_type"].str.contains("LIS", case=False, na=False)]
    df["bbl"]     = df["bbl"].str.zfill(10)
    df["lp_date"] = pd.to_datetime(df["document_date"]).dt.date
    return df[["bbl", "lp_date"]]



