import numpy as np
import os.path
import pandas as pd
import sys

import database

def main():
    """
    python3 add_ogle3.py rrab.sqlite ogle4 lmc lmc.csv curves/
    """
    database_file = sys.argv[1]
    survey = sys.argv[2]
    cluster = sys.argv[3]
    catalog_file = sys.argv[4]
    curves_dir = sys.argv[5]

    oost = "Unlabled"
    survey_info = pd.read_csv(catalog_file)

    lc_ids = np.array(survey_info["id"])
    periods = np.array(survey_info["period"])

    data = np.column_stack((lc_ids, periods))

    def process_data(cur):
        database.add_survey(cur,survey, cluster, oost)

        for row in data:
            i = row[0]
            period = row[1]

            database.add_star(cur, i, survey, cluster, period)

            for band in ["I", "V"]:
                try:
                    curve = get_light_curve(curves_dir, band, i)

                    database.add_light_curve(cur, i, survey, cluster, band,
                            curve)
                except FileNotFoundError:
                    pass

    database.with_database(database_file, process_data)

def get_light_curve(curves_dir, band, i):
    """
    Return the light curve for the object with the given id inthe given band,
    using the corresponding .csv file in the given light curves directory.
    """
    lc_file = os.path.join(curves_dir, band, i + ".csv")
    print(lc_file)
    curve = pd.read_csv(lc_file)

    return curve.as_matrix(["time","mag","magerror"])

if __name__ == "__main__":
    main()
