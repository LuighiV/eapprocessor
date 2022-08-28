from pathlib import Path
import pandas as pd
import numpy as np


def parse_lcadc(filepath, time_threshold=1e-8, t_start=None, t_stop=None):
    df = pd.read_csv(Path(filepath), comment=';', header=None,
                     names=["time_VOUT", "VOUT"])
    df["delayed"] = df["VOUT"].shift(periods=1, fill_value=0)
    df["abs_diff"] = np.absolute(df["VOUT"] - df["delayed"])

    ndf = df.loc[df["abs_diff"] != 0].copy()
    ndf["time_diff"] = ndf["time_VOUT"].shift(
        periods=-1, fill_value=0) - ndf["time_VOUT"]
    sel_df = ndf.loc[ndf["time_diff"] > time_threshold].copy()

    if t_start is not None:
        sel_df = sel_df[(sel_df["time_VOUT"] >= t_start)].copy()

    if t_stop is not None:
        sel_df = sel_df[(sel_df["time_VOUT"] <= t_stop)].copy()

    return np.array(sel_df["time_VOUT"]), np.array(sel_df["VOUT"])
