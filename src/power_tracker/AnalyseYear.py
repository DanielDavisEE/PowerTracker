import csv
import statistics
from datetime import datetime, timedelta

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

DAYS_IN_YEAR = 365  # days/year
HOURS_IN_DAY = 24  # hours/day
MINS_IN_HOUR = 60  # mins/hour
SECS_IN_MIN = 60  # secs/min
TIMESTEP = 30  # mins


def daterange(start, end, step):
    tmp = start
    while tmp < end:
        yield tmp
        tmp += step


def get_day(data, day):
    index = (day * HOURS_IN_DAY * MINS_IN_HOUR) // TIMESTEP
    return data[index: index + (HOURS_IN_DAY * MINS_IN_HOUR) // TIMESTEP]


def create_timeseries():
    max_timesteps = (DAYS_IN_YEAR * HOURS_IN_DAY * MINS_IN_HOUR) // TIMESTEP
    with open('Demand by a Region.csv', 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        stacked_power = [[] for _ in range(max_timesteps)]
        timestep = 0
        firstLoop = True
        for point in reader:
            dt = datetime.strptime(point['Trading Period Start Date & Time'], '%d/%m/%Y %H:%M')
            power = float(''.join(x for x in point['NZ'] if x != ','))

            if firstLoop:
                timestep = int(dt.timestamp() - datetime(dt.year, 1, 1).timestamp()) // (SECS_IN_MIN * TIMESTEP)
                tmp = timedelta(minutes=timestep * TIMESTEP)
                first_time = dt
                firstLoop = False

            stacked_power[timestep].append(power)
            timestep += 1
            if timestep == max_timesteps:
                timestep = 0

    return [statistics.mean(n) for n in stacked_power]


if __name__ == "__main__":
    average_power = create_timeseries()
    times = daterange(datetime(2019, 1, 1), datetime(2020, 1, 1), timedelta(minutes=TIMESTEP))

    today = (datetime.now() - datetime(datetime.now().year, 1, 1)).days
    day_data = get_day(average_power, today)
    day_times = daterange(datetime.now(), datetime.now() + timedelta(days=1), TIMESTEP)
    for time, power in zip(day_times, day_data):
        print(f'{time.strftime("%Y-%m-%d %H:%M")}\t {power}')

    fig, ax = plt.subplots()

    locator = mdates.AutoDateLocator()  # minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)

    ax.set_ylabel('Power (MW)')
    ax.set_ylim([0, 5500])

    ax.plot(matplotlib.dates.date2num(day_times), day_data)
    plt.show()
