import os, requests, datetime as dt, pandas as pd

def run():
    since = (dt.date.today() - dt.timedelta(days=90)).isoformat()
    url = (
        "https://data.cityofnewyork.us/resource/bnx9-e6tj.json"
        f"?$select=bbl,document_date&$where=document_type_code='LP'"
        f" AND document_date>='{since}'&$limit=50000"
    )
    r = requests.get(url, headers={"X-App-Token": os.getenv("NYC_APP_TOKEN")})
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["bbl"] = df["bbl"].str.zfill(10)
    df["lp_date"] = pd.to_datetime(df["document_date"]).dt.date
    return df[["bbl", "lp_date"]]
