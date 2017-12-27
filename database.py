import sqlite3
import sys

try:
    import cPickle as pickle
except:
    import pickle

def with_database(database_file, function):
    con = sqlite3.connect(database_file)
    cur = con.cursor()

    function(cur)

    con.commit()
    con.close()

def add_survey(cur, survey, cluster, oost):
    cur.execute("INSERT INTO Surveys VALUES (?, ?, ?)",
        (survey, cluster, oost)
    )

def add_star(cur, lc_id, survey, cluster, period):
    cur.execute("INSERT INTO Stars VALUES (?, ?, ?, ?, ?, ?)",
        (lc_id, survey, cluster, period, None, None)
    )

def add_light_curve(cur, lc_id, survey, cluster, band, curve):
    cur.execute("INSERT INTO LightCurves VALUES (?, ?, ?, ?, ?)",
        (lc_id, survey, cluster, band, pack_curve(curve))
    )

def pack_curve(curve):
    return sqlite3.Binary(pickle.dumps(curve, protocol=2))

def unpack_curve(curve_pickle):
    return pickle.loads(bytes(curve_pickle[0]))
