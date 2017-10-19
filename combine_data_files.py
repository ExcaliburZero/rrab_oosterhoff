import numpy as np
import pandas as pd

COMMON_COLUMNS = ["id", "period", "I_amp", "V_amp"]
CLUSTER_COL = "cluster"
PAPER_COL = "paper"
OOST_COL = "oost_group"

def main():
    data = pd.concat([
        omega_cen_braga(),
        m15_corwin(),
        m5_ferro(),
        m68_kains()
    ])

    data["period"] = data["period"].map(str_to_float)
    data["I_amp"] = data["I_amp"].map(str_to_float)
    data["V_amp"] = data["V_amp"].map(str_to_float)

    print(data)

    data.to_csv("combined.csv", index=False)

def omega_cen_braga():
    data_file = "Omega_Cen_RR_Lyrae/J_AJ_152_170/table_2_and_3.csv"

    data = pd.read_csv(data_file)
    columns = ["Name", "Per1", "AI", "AV1"]

    category_col = "Mode"
    rr_ab = "RRab"

    data = data[data[category_col] == rr_ab]

    data = data[columns]
    data.columns = COMMON_COLUMNS

    data[CLUSTER_COL] = "omega_cen"
    data[PAPER_COL] = "Braga 2016"
    data[OOST_COL] = "Many?"

    return data

def m15_corwin():
    data_file = "M15/asu.csv"

    data = pd.read_csv(data_file)
    columns = ["Name", "Per", "Iamp", "Vamp"]

    category_col = "Type"
    rr_ab = "RR0"

    data = data[data[category_col] == rr_ab]

    data = data[columns]
    data.columns = COMMON_COLUMNS

    data[CLUSTER_COL] = "M15"
    data[PAPER_COL] = "Corwin 2008"
    data[OOST_COL] = "II"

    return data

def m5_ferro():
    data_file = "M5/Ferro_2016/asu.csv"

    data = pd.read_csv(data_file)
    columns = ["VName", "Per", "AI", "AV"]

    category_col = "VType"
    rr_ab = "RRab"

    data[category_col] = data[category_col].map(lambda s: s.strip())

    # What about RRab Bl (?)
    data = data[data[category_col] == rr_ab]

    data = data[columns]
    data.columns = COMMON_COLUMNS

    data[CLUSTER_COL] = "M5"
    data[PAPER_COL] = "Ferro 2016"
    data[OOST_COL] = "I"

    return data

def m68_kains():
    data_file = "M68/Kains_2015/asu.csv"

    data = pd.read_csv(data_file)
    columns = ["VName", "Per", "Iamp", "Vamp"]

    category_col = "VType"
    rr_ab = "RR0"

    data[category_col] = data[category_col].map(lambda s: s.strip())

    # Is RR0 == RRab (?)
    data = data[data[category_col] == rr_ab]

    data = data[columns]
    data.columns = COMMON_COLUMNS

    data[CLUSTER_COL] = "M68"
    data[PAPER_COL] = "Kains 2015"
    data[OOST_COL] = "II"

    return data


def str_to_float(s):
    try:
        return float(s)
    except ValueError:
        return np.nan

if __name__ == "__main__":
    main()
