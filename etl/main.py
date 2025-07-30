import os, datetime as dt, pandas as pd
from fetch_acris_lp import run as get_acris
from fetch_nyc_liens import run as get_liens
from fetch_hpd_violations import run as get_viol
from fetch_hpd_vacate import run as get_vac
from fetch_nassau_lp import run as get_nassau
from merge_score import run as merge_score

os.makedirs("outputs", exist_ok=True)
today = dt.date.today()

acris  = get_acris()
liens  = get_liens()
viols  = get_viol()
vacate = get_vac()
nassau = get_nassau()

merge_score(acris, liens, viols, vacate, nassau)
print("Pipeline complete:", today)
