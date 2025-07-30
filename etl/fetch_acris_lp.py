import os, requests, datetime as dt, pandas as pd, urllib.parse as up

API = "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"

def run():
    token = os.getenv("NYC_APP_TOKEN")
    if not token or len(token) < 20:
        raise RuntimeError("NYC_APP_TOKEN env‑var missing or too short")

    since = (dt.date.today() - dt.timedelta(days=90)).strftime("%Y-%m-%dT00:00:00")

    params = {
    "$select": "document_date,doc_type,recorded_borough,block,lot",   # ← COMMA here
    "$where": f"document_date >= '{since}'",                          # ← COMMA here
    "$limit": 50000,                                                  # ← COMMA here
    "$$app_token": token                                              # ← last item, no comma
}


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

    # keep only Lis Pendens rows (any variant)
df = df[df["doc_type"].str.contains("LIS", case=False, na=False)]

# build a zero‑padded 10‑digit BBL from borough / block / lot
df["bbl"] = (
    df["recorded_borough"].str.zfill(1)
    + df["block"].str.zfill(5)
    + df["lot"].str.zfill(4)
)

# convert date to python date
df["lp_date"] = pd.to_datetime(df["document_date"]).dt.date

print(f"Acris LP rows kept: {len(df)}")
return df[["bbl", "lp_date"]]





