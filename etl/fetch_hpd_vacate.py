import os, requests, pandas as pd

def run():
    API = "https://data.cityofnewyork.us/resource/tb8q-a3ar.json"
    token = os.getenv("NYC_APP_TOKEN")
    params = {
        "$where":      "actual_rescind_date IS NULL",
        "$select":     "bbl",
        "$limit":      50000,
        "$$app_token": token,
    }
    r = requests.get(API, params=params, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["vacate_flag"] = 1
    return df[["bbl", "vacate_flag"]]
