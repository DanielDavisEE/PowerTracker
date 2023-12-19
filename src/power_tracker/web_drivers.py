import csv
import io
import logging
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

from file_utils import ReversedFile, create_file

LOG = logging.getLogger('WebDriver')

LIVE_DATA_URL = 'https://www.transpower.co.nz/system-operator/live-system-and-market-data/consolidated-live-data'
TIME_PATTERN = '(as at) %d %b %Y %H:%M'


def scrape_generation_data():
    req = requests.get(LIVE_DATA_URL)
    soup = BeautifulSoup(req.text, features="html.parser")

    power_generation_table = soup.find(class_="power-generation")
    power_generation = (
        pd.read_html(io.StringIO(str(power_generation_table)))[0]
        .set_index('Power Generation')
        .squeeze())

    current_time = datetime.strptime(power_generation.name, TIME_PATTERN)
    LOG.info(f'Scraping Generation Data ({current_time.timestamp()})')

    power_generation = (
        power_generation
        .str.split(expand=True)[0]
        .replace('0', ''))
    power_generation = power_generation.to_dict()
    power_generation['timestamp'] = current_time.timestamp()

    return power_generation


def save_generation_data(generation_data: dict):
    create_file('power_data/power_totals.csv')
    create_file('metadata/gen_sources.txt')

    current_timetamp = generation_data.pop('timestamp')

    with open('power_data/power_totals.csv', 'r') as infile:
        try:
            latest_entry = ReversedFile(infile).readline()
        except StopIteration:
            pass
        else:
            latest_timetamp = float(latest_entry.split(',', maxsplit=1)[0])
            if current_timetamp <= latest_timetamp:
                return 1

    with open('metadata/gen_sources.txt', 'r', encoding='utf-8') as infile:
        known_gen_source = infile.read().splitlines()

    # If any generation sources were scraped that haven't been seen before, add them to the
    # known_gen_source list to maintain the order in the csv.
    if set(known_gen_source) != set(generation_data):
        known_gen_source.extend([gen_source for gen_source in generation_data if gen_source not in known_gen_source])
        with open('metadata/gen_sources.txt', 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(known_gen_source))

    output_row = [current_timetamp]
    for gen_source in known_gen_source:
        output_row.append(generation_data.get(gen_source, ''))

    with open('power_data/power_totals.csv', 'a', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(output_row)

    return 0


if __name__ == '__main__':
    generation_data = scrape_generation_data()
    save_generation_data(generation_data)
