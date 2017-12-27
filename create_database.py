import sqlite3
import sys

try:
    import cPickle as pickle
except:
    import pickle

def main():
    database_file = sys.argv[1]

    con = sqlite3.connect(database_file)
    cur = con.cursor()

    create_table(cur, "Surveys", [
        "survey TEXT",
        "cluster TEXT",
        "oost TEXT",
        "PRIMARY KEY(survey, cluster)"
    ])

    create_table(cur, "LightCurves", [
        "id TEXT",
        "survey TEXT",
        "cluster TEXT",
        "band TEXT",
        "curve BLOB",
        "PRIMARY KEY(id, survey, cluster, band)"
    ])

    create_table(cur, "Stars", [
        "id TEXT",
        "survey TEXT",
        "cluster TEXT",
        "period FLOAT",
        "amplitude_I FLOAT",
        "amplitude_V FLOAT",
        "PRIMARY KEY(id, survey, cluster)"
    ])

    print(database_file)

def create_table(cur, name, fields):
    cur.execute("CREATE TABLE " + name + "(" + ", ".join(fields) + ")")

if __name__ == "__main__":
    main()
