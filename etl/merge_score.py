
import os
import pandas as pd
import requests
def enrich_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Join owner/mailing address fields from PAD onto df by BBL.
    Expects df to have a 'bbl' string column of length 10.
    """
    if df.empty or "bbl" not in df.columns:
        return df.copy()

    # Build Socrata $where: (boro=1 AND block=12345 AND lot=6789) OR ...
    conditions = []
    for bbl in df["bbl"].astype(str):
        conditions.append(
            f"(boro={int(bbl[0])} AND block={int(bbl[1:6])} AND lot={int(bbl[6:])})"
        )
    where_clause = " OR ".join(conditions)

    url = "https://data.cityofnewyork.us/resource/PadPropertyAddressDirectory.json"
    params = {
        "$select": ",".join([
            "boro","block","lot",
            "house_number","street_name","owner_name",
            "owner_address1","owner_city","owner_state","owner_zip"
        ]),
        "$where": where_clause,
        "$limit": len(df),
    }
    token = os.getenv("NYC_APP_TOKEN")
    headers = {"X-App-Token": token} if token else None

    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    addr_df = pd.DataFrame(resp.json())
    if addr_df.empty:
        return df.copy()

    # Rebuild BBL and merge
    addr_df["bbl"] = (
        addr_df["boro"].astype(int).astype(str) +
        addr_df["block"].astype(int).astype(str).str.zfill(5) +
        addr_df["lot"].astype(int).astype(str).str.zfill(4)
    )
    keep_cols = [
        "bbl","house_number","street_name","owner_name",
        "owner_address1","owner_city","owner_state","owner_zip"
    ]
    return df.merge(addr_df[keep_cols], on="bbl", how="left")












# import os
# import pandas as pd
# import requests

# def enrich_addresses(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Fetch mailing address info for a list of BBLs from NYC Property Address Directory (PAD) view.
#     """
#     API = "https://data.cityofnewyork.us/resource/DUZ4-2GN9.json"  # your PAD resource
#     token = os.getenv("NYC_APP_TOKEN")
#     params = {
#     "$select": ",".join([
#         "boro","block","lot",
#         "house_number","street_name","owner_name",
#         "owner_address1","owner_city","owner_state","owner_zip"
#     ]),
#     "$where": where,
#     "$limit": len(df),
#     }
#     headers = {"X-App-Token": token}
#     resp = requests.get(API, params=params, headers=headers, timeout=30)
#     resp.raise_for_status()
#     addr_df = pd.DataFrame(resp.json())

#     return df.merge(addr_df, on="bbl", how="left")

# def run(acris, liens, viols, vacate, nassau):
#     # 1. Build master BBL list
#     keys = pd.concat([
#         acris["bbl"],
#         liens["bbl"],
#         viols["bbl"],
#         vacate["bbl"]
#     ]).drop_duplicates().to_frame(name="bbl")

#     # 2. Merge feeds onto keys
#     df = (
#         keys
#         .merge(acris, how="left", on="bbl")
#         .merge(liens, how="left", on="bbl")
#         .merge(viols, how="left", on="bbl")
#         .merge(vacate, how="left", on="bbl")
#     )

#     # 3. Compute distress score
#     df["score"] = (
#         df["lp_date"].notna().astype(int) * 2 +
#         df["lien_flag"].fillna(0).astype(int) +
#         df["viol_flag"].fillna(0).astype(int) +
#         df["vacate_flag"].fillna(0).astype(int)
#     )

#     # 4. Append Nassau feed if present
#     if not nassau.empty:
#         nassau_copy = nassau.copy()
#         nassau_copy["score"] = 2
#         nassau_copy = nassau_copy.rename(columns={"sbl": "bbl"})
#         df = pd.concat([df, nassau_copy], ignore_index=True)

#     # 5. Filter & rank (use >=3 in production)
#     df = df[df["score"] >= 1]
#     df = df.sort_values(["score", "lp_date"], ascending=[False, False]).head(100)

#     # 6. Enrich with mailing addresses
#     try:
#         enriched_df = enrich_addresses(df)
#     except Exception as e:
#         print(f"❌  Address enrichment failed ({e.__class__.__name__}): {e}")
#         enriched_df = df.copy()

#     # 7. Ensure output directory exists
#     os.makedirs("outputs", exist_ok=True)

#     # 8. Write CSVs
#     df.to_csv("outputs/top100.csv", index=False)
#     enriched_df.to_csv("outputs/top100_enriched.csv", index=False)

#     return enriched_df


    return enriched_df
    # ... heat-map code ...
