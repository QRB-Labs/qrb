#!/usr/bin/python3
'''Feedback control loop: reads temperature from the sensor, computes
feedback signal (equivalent to a temperature forecast) and activates
the pump control (toggle_relay) to stay below threshold temperature.

Usage:

./feedback_control.py > feedback_control.log 2>&1 &

'''

from datetime import datetime
import heapq
import numpy as np
import time
import random

import qrb_logging
import relay_webapp

DRY_RUN=False  # if True, no activation, reading and simulation only
SENSOR_PERIOD = 60

# Feedback control parameraters
WINDOW = 3600            # look back to compute current rate of change
DERIVATIVE_COEFF = 900   # look forward for forecast
THRESHOLD_TEMP = 25      # target to stay under

MAX_ACTIVATIONS_PER_DAY = 48
DAY_LENGTH = 24*60*60
MAX_ACTIVATION_DURATION = 180
MIN_ACTIVATION_DURATION = 30
MTB_ACTIVATIONS = 900    # minimum time between activations

TEMP_BETA=0.0426         # °C ~smallest achievable temp change
DURATION_ALPHA=60/2.12   # seconds per log normalized temp change
Kp = 1.0/TEMP_BETA
Kd = DERIVATIVE_COEFF/TEMP_BETA
Ki = 1.0/(4*TEMP_BETA*DERIVATIVE_COEFF)


def integral(x, y):
    return np.sum(y[1:] * np.diff(x))


def slope(x, y):
    '''Least squares regression: y = a*x + b. Returns (a, b).

    '''
    X = np.vstack([x, np.ones(len(x))]).T
    a, b = np.linalg.lstsq(X, y, rcond=None)[0]
    return a, b


def slice_to_window(time_series, value_series, window_start):
    n = 0
    while n < len(time_series) and time_series[n] < window_start:
        n += 1
    return time_series[n:], value_series[n:]


def main(my_logger):
    temperature_history = np.array([])
    time_history = np.array([])
    activation_history = []
    t0 = datetime.now().timestamp()
    t = None

    while True:
        if t: # don't sleep on the first iteration
            time.sleep(SENSOR_PERIOD)
        t = datetime.now().timestamp() - t0
        temperature, humidity = relay_webapp.read_sensor()
        if temperature is None:
            my_logger.error("read_sensor failed")
            continue
        time_history, temperature_history = slice_to_window(
            np.append(time_history, t),
            np.append(temperature_history, temperature),
            t-WINDOW)
        if len(time_history) < 5:
            continue

        temp_slope, unused = slope(time_history, temperature_history)
        pred_temperature = DERIVATIVE_COEFF*temp_slope + temperature
        # Control signal u is
        # - PID (proportional, integral, derivative) of temperature error,
        # - desired normalized temp change. E.g. u = 2.0 => temp -= 2*TEMP_BETA
        u = Kp*(temperature - THRESHOLD_TEMP) + \
            Kd*temp_slope + \
            Ki*integral(time_history, np.asarray(temperature_history) - THRESHOLD_TEMP)

        my_logger.debug({"message": "Control signal",
                         "Temperature": temperature,
                         "Humidity": humidity,
                         "Control": u,
                         "Temperature Forecast": pred_temperature})

        if u < 1.0:
            # desired change < smallest achievable temp change TEMP_BETA
            continue

        while activation_history and min(activation_history) < t-DAY_LENGTH:
            heapq.heappop(activation_history)

        if len(activation_history) >= MAX_ACTIVATIONS_PER_DAY:
            my_logger.debug({"message": "Skip. Daily max."})
            continue

        if len(activation_history) and t - max(activation_history) < MTB_ACTIVATIONS:
            my_logger.debug({"message": "Skip. Max frequency."})
            continue

        # activation duration ~ log of normalized desired temperature change.
        duration = DURATION_ALPHA * np.log(u)
        duration = max(MIN_ACTIVATION_DURATION,
                       min(MAX_ACTIVATION_DURATION,
                           duration))
        duration = int(duration)
        my_logger.info({"message": "Activate",
                        "duration": duration,
                        "Temperature Forecast": pred_temperature})
        if not DRY_RUN:
            relay_webapp.toggle_relay(duration)
        heapq.heappush(activation_history, t)


if __name__ == '__main__':
    my_logger = qrb_logging.get_logger("rpi.feedback_control")
    try:
        main(my_logger)
    except Exception as e:
        my_logger.error(e)
        raise e
