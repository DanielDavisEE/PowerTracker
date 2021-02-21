import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from ReversedFile import *
from datetime import datetime, timedelta
import AnalyseMonth, csv

MINS_IN_HOUR = 60 # mins
TIMESTEP = 5 # mins

def create_graph():
    hours = 12
    max_timesteps = (hours * MINS_IN_HOUR // TIMESTEP)
    with plt.xkcd(scale=0.4, length=200, randomness=50):
    
        current_time = datetime.now()
        data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PowerData')
        with open(os.path.join(data_path, 'Total.csv'), 'r') as infile:
            reader = csv.reader(ReversedFile(infile))
            power_data = []
            offset = 0
            latest_time = None
            for _ in range(max_timesteps):
                try:
                    new_data_point = reader.__next__()
                except StopIteration:
                    new_data_point = [''] * 8
                else:
                    if latest_time is None:
                        latest_time = datetime.strptime(new_data_point[0], '%d %b %Y %H:%M')
                    
                try:
                    power = int(new_data_point[1])
                except ValueError:
                    power = -1
                finally:
                    power_data.append(power)
        
        power_data.reverse()
        times = [latest_time - timedelta(minutes=i) for i in range((max_timesteps - 1) * TIMESTEP, -1, -TIMESTEP)]
        masked_power_data = np.ma.masked_where(np.array(power_data) < 0, power_data, copy=True)
        
        fig, ax = plt.subplots(figsize=(4, 4))     
        
        locator = mdates.HourLocator(interval=3)#minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        ax.set_ylabel('Power (MW)')
        ax.set_xlabel('')
        
        ax.set_ylim([2500, 6000])
        ax.set_xlim(matplotlib.dates.date2num((times[0], times[-1])))
        
        plt.subplots_adjust(left=0.23, bottom=0.15, top=0.9)
        #times, average_power = AnalyseMonth.create_timeseries(datetime.strptime(new_data_point[0], '%d %b %Y %H:%M').date())
        ax.plot(matplotlib.dates.date2num(times), masked_power_data, 'k')
        #ax.plot(times, average_power)
        
        
    plt.savefig('PowerPlot.png', dpi=100)

if __name__ == "__main__":
    create_graph()
    plt.show()      