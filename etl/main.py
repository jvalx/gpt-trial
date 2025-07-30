import pandas as pd
import datetime as dt

from fetch_nyc_liens import run as get_liens
from fetch_hpd_violations import run as get_viol
from fetch_hpd_vacate import run as get_vac
from fetch_nassau_lp import run as get_nassau
from merge_score import run as merge_score

# import ACRIS but don’t fail if it errors
from fetch_acris_lp import run as get_acris

def main():
    today = dt.date.today()

    try:
        acris = get_acris()
    except Exception as e:
        print(f"⚠️  ACRIS fetch failed, skipping: {e}")
        acris = pd.DataFrame(columns=["bbl", "lp_date"])

    liens  = get_liens()
    viols  = get_viol()
    vacate = get_vac()
    nassau = get_nassau()

    merge_score(acris, liens, viols, vacate, nassau)
    print("Pipeline complete:", today)

if __name__ == "__main__":
    main()
