import csv
from datetime import datetime, timedelta

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from file_utils import *
from waveshare_epd.epd7in5_V2 import EPD
from pathlib import Path

MINS_IN_HOUR = 60  # mins
TIMESTEP = 5  # mins

FONT = ImageFont.truetype('Humor-Sans.ttf', 38)

V_MARGIN = 40
SCREEN = EPD()
latest_gen_data_tmp = {
    'DateTime': '3/01/2021 11:46',
    'NIWind': '88',
    'NIHydro': '759',
    'Geothermal': '921',
    'Gas-Coal': '0',
    'Gas': '375',
    'Diesel-Oil': '0',
    'Co-Gen': '157',
    'SIWind': '3',
    'SIHydro': '1880'
}
total_generation_tmp = sum(int(v.removesuffix(' MW')) for k, v in latest_gen_data_tmp.items() if k != 'DateTime')


class BBox:
    def __init__(self, image):
        self.left, self.top, self.right, self.bottom = image.getbbox()

    def __str__(self):
        return f'Bounding Box(left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom})'


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

        locator = mdates.HourLocator(interval=3)  # minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.set_ylabel('Power (MW)')
        ax.set_xlabel('')

        ax.set_ylim([2500, 6000])
        ax.set_xlim(matplotlib.dates.date2num((times[0], times[-1])))

        plt.subplots_adjust(left=0.23, bottom=0.15, top=0.9)
        # times, average_power = AnalyseMonth.create_timeseries(datetime.strptime(new_data_point[0], '%d %b %Y %H:%M').date())
        ax.plot(matplotlib.dates.date2num(times), masked_power_data, 'k')
        # ax.plot(times, average_power)

    plt.savefig('power_plot.png', dpi=100)


def create_image():
    create_graph()
    graph_image = Image.open("power_plot.png")
    graph_rect = BBox(graph_image)

    main_image = Image.new('1', (SCREEN.width, SCREEN.height), 255)
    main_image.paste(graph_image, (0, V_MARGIN))
    draw_main_image = ImageDraw.Draw(main_image)

    icons_path = Path(__file__) / 'icons'
    for i, img_name in enumerate(sorted(os.listdir(icons_path))):

        # Generation Block
        coords = (int(((SCREEN.width - graph_rect.right) // 2) * (i // 4) + graph_rect.right),
                  int(((SCREEN.height - V_MARGIN * 2) // 4) * (i % 4)) + V_MARGIN)

        # Generation Icon
        icon_image = Image.open(os.path.join(icons_path, img_name))
        icon_bbox = BBox(icon_image)
        main_image.paste(icon_image, coords)

        # Generation Value
        gen_type = img_name.removesuffix('.png')[3:]
        if gen_type in ('Wind', 'Hydro'):
            mw_generation = (float(latest_gen_data['NI' + gen_type])  # .removesuffix(' MW'))
                             + float(latest_gen_data['SI' + gen_type]))  # .removesuffix(' MW')))
        else:
            mw_generation = float(latest_gen_data[gen_type])  # .removesuffix(' MW'))
        fraction_generation = mw_generation * 100 / total_generation

        coords_text = (coords[0] + icon_bbox.right, coords[1] + icon_bbox.bottom // 2)

        draw_main_image.text(coords_text, f'{fraction_generation:.1f}%', anchor="lm", font=FONT, fill=0)

    main_image.save("tmp/screen_image.png")


if __name__ == "__main__":
    print(Path(__file__) / 'icons')
    # create_graph()
    # plt.show()
