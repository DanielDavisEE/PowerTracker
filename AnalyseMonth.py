import csv, statistics
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import time
from datetime import date
from datetime import datetime


def create_timeseries(my_day=None):
    max_timesteps = (24 * 60 // 5) - 1
    with open('LastMonth.csv', 'r') as infile:
        reader = csv.DictReader(infile, )
        stacked_power = [[] for _ in range(max_timesteps)]

        timestep, day = 0, 0
        for point in reader:
            dt = datetime.strptime(point['Date'], '%d/%m/%Y %H:%M')
            power = float(point['NZ TOTAL(MW)'])
            if timestep == 0 and day == 0:
                timestep = (dt.hour * 60 + dt.minute) // 5

            stacked_power[timestep].append(power)
            timestep += 1
            if timestep == max_timesteps:
                day += 1
                timestep = 0

    if my_day is None:
        my_day = date(2020, 12, 1)

    times = [datetime.combine(my_day, time(hour=(5 * i) // 60, minute=(5 * i) % 60)) for i in range(max_timesteps)]
    return times, [statistics.mean(n) for n in stacked_power]


if __name__ == "__main__":
    times, average_power = create_timeseries()

    for time, power in zip(times, average_power):
        print(f'{time}\t {power}')

    fig, ax = plt.subplots()

    locator = mdates.HourLocator(interval=3)  # minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_ylabel('Power (MW)')
    ax.set_ylim([0, 5500])

    ax.plot(times, average_power)
    plt.show()
