import csv
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from file_utils import *

try:
    from waveshare_epd.epd7in5_V2 import EPD_WIDTH, EPD_HEIGHT
except:
    EPD_WIDTH = 800
    EPD_HEIGHT = 480

SECS_IN_MIN = 60
MINS_IN_HOUR = 60
TIMESTEP = 5 * SECS_IN_MIN  # secs
HOURS_RANGE = 12

GRAPH_POWER_MIN = 2500
GRAPH_POWER_MAX = 6000

FONT = ImageFont.truetype('xkcd-script.ttf', 38)
V_MARGIN = 40

ICONS_FOLDER = Path(__file__).parent / 'icons'


class BBox:
    def __init__(self, image):
        self.left, self.top, self.right, self.bottom = image.getbbox()

    def __str__(self):
        return f'Bounding Box(left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom})'


def load_last_twelve_hours():
    power_generation_df = []
    latest_timestamp = None
    with open('power_data/power_totals.csv', 'r') as infile:
        reader = csv.reader(ReversedFile(infile))
        for timestamp_str, *powers in reader:
            timestamp = float(timestamp_str)
            if latest_timestamp is None:
                latest_timestamp = timestamp
                oldest_timestamp = latest_timestamp - HOURS_RANGE * MINS_IN_HOUR * SECS_IN_MIN
            elif timestamp < oldest_timestamp:
                break

            total_power = sum(int(value) if value != '' else 0 for value in powers)
            power_generation_df.append((timestamp, total_power))

    power_generation_df = pd.DataFrame(power_generation_df, columns=['timestamp', 'power'])
    power_generation_df = power_generation_df.sort_values(by='timestamp').reset_index(drop=True)

    power_generation_df['datetime'] = power_generation_df['timestamp'].apply(datetime.fromtimestamp)
    power_generation_df['np_datetime'] = matplotlib.dates.date2num(power_generation_df['datetime'])

    return power_generation_df


def create_graph():
    power_generation_df = load_last_twelve_hours()

    # Find gaps in the data and designate them as individual lines to be plotted
    line_starts = [0]
    for idx in power_generation_df.index[1:]:
        if power_generation_df.loc[idx, 'timestamp'] - power_generation_df.loc[idx - 1, 'timestamp'] > TIMESTEP * 2:
            line_starts.append(idx)

    latest_time = power_generation_df['datetime'].iat[-1]
    oldest_time = latest_time - timedelta(hours=HOURS_RANGE)

    with plt.xkcd(scale=0.4, length=200, randomness=50):
        fig, ax = plt.subplots(figsize=(4, 4))

        locator = mdates.HourLocator(interval=3)  # minticks=3, maxticks=7)
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.set_ylabel('Power (MW)')
        ax.set_xlabel('')

        ax.set_ylim([GRAPH_POWER_MIN, GRAPH_POWER_MAX])
        # Add a margin either side of the time range for visibility
        ax.set_xlim(matplotlib.dates.date2num((oldest_time - timedelta(seconds=TIMESTEP * 2),
                                               latest_time + timedelta(seconds=TIMESTEP * 2))))

        plt.subplots_adjust(left=0.23, bottom=0.15, top=0.9)

        # Plot each line from the data based on the line starting indices from before
        for i in range(len(line_starts)):
            line_start = line_starts[i]
            if i < len(line_starts) - 1:
                line_end = line_starts[i + 1] - 1
            else:
                line_end = power_generation_df.index[-1]
            line_df = power_generation_df.loc[line_start:line_end, :]
            ax.plot('np_datetime', 'power', data=line_df, color='k')

    image_path = 'tmp/power_plot.png'
    plt.savefig(image_path, dpi=100)
    return image_path


def create_image():
    graph_path = create_graph()
    graph_image = Image.open(graph_path)
    graph_rect = BBox(graph_image)

    main_image = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 255)
    main_image.paste(graph_image, (0, V_MARGIN))
    draw_main_image = ImageDraw.Draw(main_image)

    with open('metadata/gen_sources.txt', 'r', encoding='utf-8') as infile:
        gen_sources = infile.read().splitlines()
        with open('power_data/power_totals.csv', 'r') as infile:
            reader = csv.DictReader(ReversedFile(infile), ['_timestamp'] + gen_sources)
            latest_generation_data = reader.__next__()

    latest_generation_data.pop('_timestamp')
    for gen_type in latest_generation_data:
        if latest_generation_data[gen_type]:
            latest_generation_data[gen_type] = int(latest_generation_data[gen_type])
        else:
            latest_generation_data[gen_type] = 0

    total_generation = sum(latest_generation_data.values())
    gen_types_ordered = sorted(latest_generation_data.keys(), key=lambda k: latest_generation_data[k], reverse=True)

    for i, gen_type in enumerate(gen_types_ordered):
        # Generation Block
        coords = (int(((EPD_WIDTH - graph_rect.right) // 2) * (i // 4) + graph_rect.right),
                  int(((EPD_HEIGHT - V_MARGIN * 2) // 4) * (i % 4)) + V_MARGIN)

        # Generation Icon
        icon_file = (ICONS_FOLDER / gen_type).with_suffix('.png')
        if icon_file.exists():
            icon_image = Image.open(icon_file)
        else:
            # As a temporary fallback, just use the first three letters
            icon_image = Image.new('1', (100, 100), 255)
            draw_icon_image = ImageDraw.Draw(icon_image)
            draw_icon_image.text((20, 50), gen_type[:3], anchor="lm", font=FONT, fill=0)

        icon_bbox = BBox(icon_image)
        main_image.paste(icon_image, coords)

        # Generation Value
        generation = latest_generation_data[gen_type]
        fraction_generation = generation * 100 / total_generation

        text_coords = (coords[0] + icon_bbox.right, coords[1] + icon_bbox.bottom // 2)
        draw_main_image.text(text_coords, f'{fraction_generation:.1f}%', anchor="lm", font=FONT, fill=0)

    main_image.save('tmp/screen_image.png')


if __name__ == "__main__":
    create_image()
