import pandas as pd, geopandas as gpd, os
import requests   

import os, requests, pandas as pd

def enrich_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fetch mailing address info for a list of BBLs from NYC Property Address Directory (PAD) view.
    """
    token = os.getenv("NYC_APP_TOKEN")
    if not token:
        raise RuntimeError("NYC_APP_TOKEN is missing or invalid")

    API = "https://data.cityofnewyork.us/resource/bc8t-ecyu.json"
    # Build a SoQL IN-list of quoted BBLs
    bbl_list = "', '".join(df["bbl"])
    where_clause = f"bbl IN ('{bbl_list}')"

    params = {
        "$select": ",".join([
            "bbl",
            "house_number",
            "street_name",
            "owner_name",
            "owner_address1",
            "owner_city",
            "owner_state",
            "owner_zip"
        ]),
        "$where": where_clause,
        "$limit": len(df),
    }
    headers = {"X-App-Token": token}
    response = requests.get(API, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    addr_df = pd.DataFrame(response.json())
    # Merge mailing info back into the main DataFrame
    return df.merge(addr_df, on="bbl", how="left")


def run(acris, liens, viols, vacate, nassau):
    # 1. Build a master list of BBLs from all NYC feeds
    keys = pd.concat([
        acris["bbl"],
        liens["bbl"],
        viols["bbl"],
        vacate["bbl"]
    ]).drop_duplicates().to_frame(name="bbl")

    # 2. Left-merge each feed onto that master key list
    df = keys \
        .merge(acris,  how="left", on="bbl") \
        .merge(liens,  how="left", on="bbl") \
        .merge(viols,  how="left", on="bbl") \
        .merge(vacate, how="left", on="bbl")

    # 3. Compute Score
    df["score"] = (
        df["lp_date"].notna().astype(int) * 2 +
        df["lien_flag"].fillna(0).astype(int) +
        df["viol_flag"].fillna(0).astype(int) +
        df["vacate_flag"].fillna(0).astype(int)
    )

    # 4. Append Nassau (with its own scoring)
    if not nassau.empty:
        nassau["score"] = 2
    df = pd.concat([df, nassau.rename(columns={"sbl":"bbl"})], ignore_index=True)

    # 5. Filter & rank
    df = df[df["score"] >= 1]
    df = df.sort_values(["score", "lp_date"], ascending=[False, False]).head(100)
    
     
 
    # ensure outputs dir
    os.makedirs("outputs", exist_ok=True)

    
    # Attempt enrichment
    try:
        enriched = enrich_addresses(df)
    except Exception as e:
        print(f"❌  Address enrichment failed, skipping: {e}")
        enriched = df.copy()

    
    # write both the plain and enriched outputs (optional)
    df.to_csv("outputs/top100.csv", index=False)
    enriched.to_csv("outputs/top100_enriched.csv", index=False)
    return enriched
    # ... heat-map code ...
