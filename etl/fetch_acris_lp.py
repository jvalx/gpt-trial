import os, requests, datetime as dt, pandas as pd, urllib.parse as up

API = "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"

def run():
    token = os.getenv("NYC_APP_TOKEN")
    if not token or len(token) < 20:
        raise RuntimeError("NYC_APP_TOKEN env‑var missing or too short")

    since = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00")

    params = {}
    params["$select"]      = "bbl,document_date,document_type"
    params["$where"]       = f"document_date >= '{since}'"
    params["$limit"]       = 50000
    params["$$app_token"]  = token  # Socrata looks for this exact key

    # ----- DEBUG: print the URL without the token -----
    dbg = {k:v for k,v in params.items() if k != "$$app_token"}
    print("ACRIS URL:", API + "?" + up.urlencode(dbg, safe=":,>= '"))
    # ---------------------------------------------------

    r = requests.get(API, params=params, timeout=30)
    r.raise_for_status()

    df = pd.DataFrame(r.json())
    if df.empty:
        print("Acris LP: 0 rows (last 90d)")
        return pd.DataFrame(columns=["bbl", "lp_date"])

    df = df[df["document_type"].str.contains("LIS", case=False, na=False)]
    df["bbl"]     = df["bbl"].str.zfill(10)
    df["lp_date"] = pd.to_datetime(df["document_date"]).dt.date
    print(f"Acris LP rows kept: {len(df)}")
    return df[["bbl", "lp_date"]]





