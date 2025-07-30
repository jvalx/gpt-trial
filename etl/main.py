import pandas as pd
import datetime as dt

from fetch_acris_lp       import run as get_acris
from fetch_nyc_liens      import run as get_liens
from fetch_hpd_violations import run as get_viol
from fetch_hpd_vacate     import run as get_vac
from fetch_nassau_lp      import run as get_nassau
from merge_score          import run as merge_score

def main():
    today = dt.date.today()

    try:
        acris = get_acris()
    except Exception as e:
        print(f"⚠️  ACRIS fetch failed, skipping: {e}")
        acris = pd.DataFrame(columns=["bbl", "lp_date"])

    try:
        liens = get_liens()
    except Exception as e:
        print(f"⚠️  Liens fetch failed, skipping: {e}")
        liens = pd.DataFrame(columns=["bbl", "total_due", "cycle", "lien_flag"])

    try:
        viols = get_viol()
    except Exception as e:
        print(f"⚠️  Violations fetch failed, skipping: {e}")
        viols = pd.DataFrame(columns=["bbl", "open_c_count", "viol_flag"])

    try:
        vacate = get_vac()
    except Exception as e:
        print(f"⚠️  Vacate fetch failed, skipping: {e}")
        vacate = pd.DataFrame(columns=["bbl", "vacate_flag"])

    try:
        nassau = get_nassau()
    except Exception as e:
        print(f"⚠️  Nassau LP fetch failed, skipping: {e}")
        nassau = pd.DataFrame(columns=["sbl", "record_dt", "lp_flag"])

    merge_score(acris, liens, viols, vacate, nassau)
    print("Pipeline complete:", today)

if __name__ == "__main__":
    main()

