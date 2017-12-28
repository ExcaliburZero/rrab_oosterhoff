from functools import partial
from scipy.optimize import leastsq
from scipy import stats

import math
import numpy as np
import sys

import database

ERROR_THRESHOLD = 0.2
STD_THRESHOLD = 2.0
ITERATIONS = 5

FOURIER_ORDER = 1
AMPLITUDE_OF_FOURIER = False

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
                    print(band)
                    curve = get_light_curve(cur2, i, survey, cluster, band)

                    for c in curve:
                        lc = database.unpack_curve(c)

                        results = process((lc, period))

                        save_results(cur, s, band, results)

                print("")

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

    print(period_shifted.shape[0])

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

    return np.column_stack((shifted_times, mags, magerrs))

def get_amplitude(curve):
    times = curve[:,0]
    mags = curve[:,1]

    fourier_order = FOURIER_ORDER

    fourier_coef = fourier_decomposition(times, mags, fourier_order)
    #amplitude = fourier_R(fourier_coef, 1)

    spaced_times = np.arange(0.0, 1.0, 0.001)
    values = fourier_series(spaced_times, fourier_coef, fourier_order)

    #print("mags: ", stats.describe(mags))
    #print("")
    #print("fourier: ", stats.describe(values))

    if not AMPLITUDE_OF_FOURIER:
        values = mags

    largest = np.max(values)
    smallest = np.min(values)

    print("min: ", smallest)
    print("max: ", largest)

    amplitude = largest - smallest

    return amplitude

def fourier_decomposition(times, magnitudes, order):
    """
    Fits the given light curve to a cosine fourier series of the given order
    and returns the fit amplitude and phi weights. The coefficents are
    calculated using a least squares fit.
    The fourier series that is fit is the following:
    n = order
    f(time) = A_0 + sum([A_k * cos(2pi * k * time + phi_k) for k in range(1, n + 1)])
    The fourier coeeficients are returned in a list of the following form:
    [A_0, A_1, phi_1, A_2, phi_2, ...]
    Each of the A coefficients will be positive.
    The number of (time, magnitude) values provided must be greater than or
    equal to the order * 2 + 1. This is a requirement of the least squares
    function used for calculating the coefficients.
    Parameters
    ----------
    times : numpy.ndarray
        The light curve times.
    magnitudes : numpy.ndarray
        The light curve magnitudes.
    order : int
        The order of the fourier series to fit.
    Returns
    -------
    fourier_coef : numpy.ndarray
        The fit fourier coefficients.
    """
    #times = times[:,0]
    #magnitudes = magnitudes[:,0]

    num_examples = times.shape[0]
    num_coef = order * 2 + 1

    if num_coef > num_examples:
        raise Exception("Too few examples for the specified order. Number of examples must be at least order * 2 + 1. Required: %d, Actual: %d" % (num_coef, num_examples))

    initial_coef = np.ones(num_coef)

    cost_function = partial(fourier_series_cost, times, magnitudes, order)

    fitted_coef, success = leastsq(cost_function, initial_coef)

    final_coef = correct_coef(fitted_coef, order)

    return final_coef

def correct_coef(coef, order):
    """
    Corrects the amplitudes in the given fourier coefficients so that all of
    them are positive.
    This is done by taking the absolute value of all the negative amplitude
    coefficients and incrementing the corresponding phi weights by pi.
    Parameters
    ----------
    fourier_coef : numpy.ndarray
        The fit fourier coefficients.
    order : int
        The order of the fourier series to fit.
    Returns
    -------
    cor_fourier_coef : numpy.ndarray
        The corrected fit fourier coefficients.
    """
    coef = coef[:]
    for k in range(order):
        i = 2 * k + 1
        if coef[i] < 0.0:
            coef[i] = abs(coef[i])
            coef[i + 1] += math.pi

    return coef

def fourier_series_cost(times, magnitudes, order, coef):
    """
    Returns the error of the fourier series of the given order and coefficients
    in modeling the given light curve.
    Parameters
    ----------
    times : numpy.ndarray
        The light curve times.
    magnitudes : numpy.ndarray
        The light curve magnitudes.
    order : int
        The order of the fourier series to fit.
    fourier_coef : numpy.ndarray
        The fit fourier coefficients.
    Returns
    -------
    error : numpy.float64
        The error of the fourier series in modeling the curve.
    """
    return magnitudes - fourier_series(times, coef, order)

def fourier_series(times, coef, order):
    """
    Returns the magnitude values given by applying the fourier series described
    by the given order and coefficients to the given time values.
    Parameters
    ----------
    times : numpy.ndarray
        The light curve times.
    order : int
        The order of the fourier series to fit.
    fourier_coef : numpy.ndarray
        The fit fourier coefficients.
    Returns
    -------
    magnitudes : numpy.ndarray
        The calculated light curve magnitudes.
    """
    cos_vals = [coef[2 * k + 1] * np.cos(2 * np.pi * (k + 1) * times + coef[2 * k + 2])
            for k in range(order)]
    cos_sum = np.sum(cos_vals, axis=0)

    return coef[0] + cos_sum

def fourier_R(coef, n):
    return coef[2 * (n - 1) + 1]

if __name__ == "__main__":
    main()
