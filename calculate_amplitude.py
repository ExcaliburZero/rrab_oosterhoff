def main():
    """
    light_curve = numpy vector where dim 1 are the observations and in dim 2
    there are time mag magerr
    """
    light_curves = get_light_curves()

    results = [process(lc) for lc in light_curves]

    save_results(results)

def get_light_curves():
    pass

def save_results(results):
    print(results)

    pass

def process(lc):
    curve = lc[0]
    period = lc[1]

    processed_curve = pre_process_lc(curve, error_threshold, std_threshold, iterations)
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
        std_bel = mean + std_val

        filtered = curve[np.logical_and(
            curve[:,1] > std_bel,
            curve[:,1] < std_abv
        ]

        return iterative_std_filter(filtered, std_threshold, iterations - 1)

def period_shift(light_curve, period):
    times = light_curve[:,0]
    shifted_times = times % period

    mags = light_curve[:,1]
    magerrs = light_curve[:,2]

    return np.concatenate((shifted_times, mags, magerrs), axis=1)

def get_amplitude(light_curve):
    pass

if __name__ == "__main__":
    main()
