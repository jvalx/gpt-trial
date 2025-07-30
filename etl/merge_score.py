import pandas as pd, geopandas as gpd

def run(acris, liens, viols, vacate, nassau):
    # NYC merge on BBL
    df = acris.merge(liens,  how="left", on="bbl") \
              .merge(viols,  how="left", on="bbl") \
              .merge(vacate, how="left", on="bbl")

    df["score"] = (
        df["lp_date"].notna().astype(int) * 2 +
        df["lien_flag"].fillna(0) +
        df["viol_flag"].fillna(0) +
        df["vacate_flag"].fillna(0)
    )

    # Nassau merge on S‑B‑L
    nassau["score"] = 2  # only LP so far
    # TODO: add Nassau lien/viol equivalents if desired

    df = pd.concat([df, nassau.rename(columns={"sbl": "bbl"})], ignore_index=True)
    df = df[df["score"] >= 3]
    df = df.sort_values(["score", "lp_date"], ascending=[False, False]).head(100)
    df.to_csv("outputs/top100.csv", index=False)

    # Quick heat‑map (zip‑level) — stub
    # ... gpd code here ...

    # save PDF to outputs/heatmap.pdf
