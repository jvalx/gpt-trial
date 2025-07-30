import os, requests, pandas as pd

def run():
    url = (
        "https://data.cityofnewyork.us/resource/tb8q-a3ar.json"
        "?$where=actual_rescind_date IS NULL"
        "&$select=bbl"
        "&$limit=50000"
    )
    r = requests.get(url, headers={"X-App-Token": os.getenv("NYC_APP_TOKEN")})
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["vacate_flag"] = 1
    return df[["bbl", "vacate_flag"]]
