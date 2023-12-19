import csv
from datetime import datetime, timedelta

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from file_utils import *
from pathlib import Path

try:
    from waveshare_epd.epd7in5_V2 import EPD_WIDTH, EPD_HEIGHT
except:
    EPD_WIDTH = 800
    EPD_HEIGHT = 480

SECS_IN_MIN = 60
MINS_IN_HOUR = 60
TIMESTEP = 5  # mins
HOURS = 12

FONT = ImageFont.truetype('Humor-Sans.ttf', 38)

V_MARGIN = 40


class BBox:
    def __init__(self, image):
        self.left, self.top, self.right, self.bottom = image.getbbox()

    def __str__(self):
        return f'Bounding Box(left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom})'


def create_graph():
    power_generation_df = []
    latest_timestamp = None
    with open('power_data/power_totals.csv', 'r') as infile:
        reader = csv.reader(ReversedFile(infile))
        for timestamp, *powers in reader:
            if latest_timestamp is None:
                latest_timestamp = timestamp
            elif timestamp < latest_timestamp - HOURS * MINS_IN_HOUR * SECS_IN_MIN:
                break

            total_power = sum(int(value) if value != '' else 0 for value in powers)
            power_generation_df.append((timestamp, total_power))

    power_generation_df = pd.DataFrame(power_generation_df, columns=['timestamp', 'power'])
    power_generation_df.sort_values(by='timestamp')

    max_timesteps = (HOURS * MINS_IN_HOUR // TIMESTEP)
    with plt.xkcd(scale=0.4, length=200, randomness=50):
        # Plot as continuous if gap between points is less than 10 minutes?

        times = [latest_time - timedelta(minutes=i) for i in range((max_timesteps - 1) * TIMESTEP, -1, -TIMESTEP)]
        masked_power_data = np.ma.masked_where(np.array(power_data) < 0, power_data, copy=True)

        fig, ax = plt.subplots(figsize=(4, 4))

        locator = mdates.HourLocator(interval=3)  # minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.set_ylabel('Power (MW)')
        ax.set_xlabel('')

        # TODO: Don't hardcode limits
        ax.set_ylim([2500, 6000])
        ax.set_xlim(matplotlib.dates.date2num((times[0], times[-1])))

        plt.subplots_adjust(left=0.23, bottom=0.15, top=0.9)
        ax.plot(matplotlib.dates.date2num(times), masked_power_data, 'k')

    plt.savefig('power_plot.png', dpi=100)


def create_image():
    create_graph()
    graph_image = Image.open("power_plot.png")
    graph_rect = BBox(graph_image)

    main_image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    main_image.paste(graph_image, (0, V_MARGIN))
    draw_main_image = ImageDraw.Draw(main_image)

    with open('metadata/gen_sources.txt', 'r', encoding='utf-8') as infile:
        csv_fieldnames = infile.read().splitlines()
        with open('power_data/power_totals.csv', 'r') as infile:
            reader = csv.DictReader(ReversedFile(infile), csv_fieldnames)

    icons_path = Path(__file__) / 'icons'
    for i, img_name in enumerate(sorted(os.listdir(icons_path))):

        # Generation Block
        coords = (int(((EPD_WIDTH - graph_rect.right) // 2) * (i // 4) + graph_rect.right),
                  int(((EPD_HEIGHT - V_MARGIN * 2) // 4) * (i % 4)) + V_MARGIN)

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
    create_graph()
    # plt.show()
