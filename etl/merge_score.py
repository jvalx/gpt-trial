import pandas as pd, geopandas as gpd, os

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
    df.to_csv("outputs/top100.csv", index=False)

    # ... heat-map code ...
