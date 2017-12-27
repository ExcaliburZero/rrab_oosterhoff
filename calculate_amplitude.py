import numpy as np
import sys

import database

ERROR_THRESHOLD = 1.0
STD_THRESHOLD = 3.0
ITERATIONS = 5

def main():
    """
    light_curve = numpy vector where dim 1 are the observations and in dim 2
    there are time mag magerr

    python3 calculate_amplitude.py rrab.sqlite
    """
    database_file = sys.argv[1]

    def process_data(cur):
        stars = get_stars_with_no_amplitudes(cur)

        def process_curves(cur2):
            for s in stars:
                i = s[0]
                survey = s[1]
                cluster = s[2]
                period = s[3]

                print(i, cluster, survey, period)

                for band in ["I", "V"]:
                    curve = get_light_curve(cur2, i, survey, cluster, band)

                    for c in curve:
                        lc = database.unpack_curve(c)
                        print(lc)

                        results = process((lc, period))

                        save_results(cur, s, band, results)
                        sys.exit()

        database.with_database(database_file, process_curves)

    database.with_database(database_file, process_data)

def get_stars_with_no_amplitudes(cur):
    """
    Returns the information of all of the stars that do not have their
    amplitudes calculated.
    """
    cur.execute("SELECT * FROM Stars WHERE (amplitude_I IS NULL OR amplitude_V IS NULL) AND period IS NOT NULL")

    return cur

def get_light_curve(cur, i, survey, cluster, band):
    cur.execute("SELECT curve FROM LightCurves WHERE id == ? AND survey == ? AND cluster == ? AND band == ?",
        (i, survey, cluster, band)
    )

    return cur

def save_results(cur, s, band, results):
    print(results)

    pass

def process(lc):
    curve = lc[0]
    period = lc[1]

    processed_curve = pre_process_lc(curve, ERROR_THRESHOLD, STD_THRESHOLD, ITERATIONS)
    period_shifted = period_shift(processed_curve, period)
    ampl = get_amplitude(period_shifted)

    return ampl

def pre_process_lc(curve, error_threshold, std_threshold, iterations):
    error_filtered = filter_high_error(curve, error_threshold)
    std_filtered = iterative_std_filter(error_filtered, std_threshold, iterations)

    return std_filtered

def filter_high_error(curve, error_threshold):
    return curve[curve[:,2] < error_threshold]

def iterative_std_filter(curve, std_threshold, iterations):
    if iterations == 0:
        return curve
    else:
        std = np.std(curve[:,1])
        mean = np.mean(curve[:,1])

        std_val = std * std_threshold

        std_abv = mean + std_val
        std_bel = mean - std_val

        filtered = curve[np.logical_and(
            curve[:,1] > std_bel,
            curve[:,1] < std_abv
        )]

        return iterative_std_filter(filtered, std_threshold, iterations - 1)

def period_shift(light_curve, period):
    times = light_curve[:,0]
    shifted_times = times % period

    mags = light_curve[:,1]
    magerrs = light_curve[:,2]

    return np.concatenate((shifted_times, mags, magerrs), axis=0)

def get_amplitude(light_curve):
    pass

if __name__ == "__main__":
    main()
