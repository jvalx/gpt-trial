import os, requests, datetime as dt, pandas as pd

def run():
    since = (dt.date.today() - dt.timedelta(days=365)).isoformat()
    url = (
        "https://data.cityofnewyork.us/resource/wvxf-dwi5.json"
        f"?$where=class='C' AND violationstatus='Open'"
        f" AND inspectiondate>='{since}'"
        "&$select=boro,block,lot,violationid"
        "&$limit=500000"
    )
    r = requests.get(url, headers={"X-App-Token": os.getenv("NYC_APP_TOKEN")})
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["bbl"] = (
        df["boro"].str[0].map({"M": "1", "B": "3", "K": "3", "X": "2", "Q": "4"})
        + df["block"].str.zfill(5)
        + df["lot"].str.zfill(4)
    )
    vc = df.groupby("bbl").size().rename("open_c_count").reset_index()
    vc = vc[vc["open_c_count"] >= 10]
    vc["viol_flag"] = 1
    return vc
