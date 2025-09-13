#!/usr/bin/python3
'''Feedback control loop: reads temperature from the sensor, computes
feedback signal (equivalent to a temperature forecast) and activates
the pump control (toggle_relay) to stay below threshold temperature.

'''

from datetime import datetime
import heapq
import numpy as np
import time
import random

import qrb_logging
import relay_webapp

DRY_RUN=True  # if True, no activation, reading and simulation only

SENSOR_PERIOD = 60

# Feedback control parameraters
WINDOW = 3600            # look back to compute current rate of change
DERIVATIVE_COEFF = 900   # look forward for forecast
PROPORTIONAL_COEFF = 1   # weight of current temp
THRESHOLD_TEMP = 22      # forecast threshold to activate

MAX_ACTIVATIONS_PER_DAY = 6
DAY_LENGTH = 24*60*60
ACTIVATION_DURATION = 120
MTB_ACTIVATIONS = 1800    # minimum time between activations


def slope(x, y):
    '''Least squares regression on time series: y = a*x + b where y is the
    time_series and x is it's integer index. Returns slope and
    intercept (a, b).

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

    while True:
        t = datetime.now().timestamp() - t0
        temperature, humidity = relay_webapp.read_sensor()
        if temperature is None:  # read_sensor failed
            time.sleep(SENSOR_PERIOD)
            continue
        time_history, temperature_history = slice_to_window(
            np.append(time_history, t),
            np.append(temperature_history, temperature),
            t-WINDOW)
        if len(time_history) < 3:
            time.sleep(SENSOR_PERIOD)
            continue
        a, unused = slope(time_history, temperature_history)
        pred_temperature = DERIVATIVE_COEFF*a + PROPORTIONAL_COEFF*temperature
        my_logger.info({"message": "Control signal",
                        "Temperature Forecast": pred_temperature})

        if pred_temperature > THRESHOLD_TEMP:
            if (not activation_history ) or \
               (len(activation_history) < MAX_ACTIVATIONS_PER_DAY and \
                t - max(activation_history) > MTB_ACTIVATIONS):
                my_logger.info("Activate")
                if not DRY_RUN:
                    relay_web_app.toggle_relay(ACTIVATION_DURATION)
                heapq.heappush(activation_history, t)
            else:
                my_logger.debug("Too many activations, skipping")

        while len(activation_history) > 0 and \
              min(activation_history) < t - DAY_LENGTH:
            heapq.heappop(activation_history)

        time.sleep(SENSOR_PERIOD)


if __name__ == '__main__':
    my_logger = qrb_logging.get_logger("rpi.feedback_control")
    try:
        main(my_logger)
    except Exception as e:
        my_logger.error(e)
        raise e
