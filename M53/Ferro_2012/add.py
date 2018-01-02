import numpy as np
import os.path
import pandas as pd
import sys

sys.path.append("../..")
import database

def main():
    """
    python3 add.py ../../rrab.sqlite RRab.csv curves.csv
    """
    database_file = sys.argv[1]
    survey = "Ferro_2012"
    cluster = "M53"
    catalog_file = sys.argv[2]
    curves_file = sys.argv[3]

    oost = "II"
    survey_info = pd.read_csv(catalog_file)

    ID = "VName"
    PERIOD = "Per"

    lc_ids = np.array([i.strip() for i in survey_info[ID]])
    periods = np.array(survey_info[PERIOD])

    data = np.column_stack((lc_ids, periods))

    def process_data(cur):
        database.add_survey(cur, survey, cluster, oost)

        for row in data:
            i = row[0]
            period = row[1]

            database.add_star(cur, i, survey, cluster, period)

            curves = pd.read_csv(curves_file)

            for band in ["I", "V"]:
                curve = get_light_curve(curves, band, i)

                print(i, band)
                database.add_light_curve(cur, i, survey, cluster, band,
                        curve)

    database.with_database(database_file, process_data)

def get_light_curve(curves, band, i):
    """
    Return the light curve for the object with the given id in the given band.
    """
    curve = curves[np.logical_and(curves["VName"] == i, curves["Filter"] == band)]

    return curve.as_matrix(["HJD","maginst","e_maginst"])

if __name__ == "__main__":
    main()
