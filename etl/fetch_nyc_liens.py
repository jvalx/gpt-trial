import os, requests, datetime as dt, pandas as pd

def run():
    # lien list cycles: 90‑, 60‑, 30‑, 10‑day
    url = (
        "https://data.cityofnewyork.us/resource/9rz4-mjek.json"
        "?$select=borough,block,lot,total_due,lien_type,cycle"
        "&$limit=50000"
    )
    r = requests.get(url, headers={"X-App-Token": os.getenv("NYC_APP_TOKEN")})
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["bbl"] = (
        df["borough"].str.zfill(1)
        + df["block"].str.zfill(5)
        + df["lot"].str.zfill(4)
    )
    df["lien_flag"] = 1
    return df[["bbl", "total_due", "cycle", "lien_flag"]]
