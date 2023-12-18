import csv
from datetime import datetime
import io

import pandas as pd
import requests
from bs4 import BeautifulSoup

LIVE_DATA_URL = 'https://www.transpower.co.nz/system-operator/live-system-and-market-data/consolidated-live-data'


def scrape_generation_data():
    # with open('generation_data.json', 'r') as infile:
    # generation_dict = json.load(infile)

    req = requests.get(LIVE_DATA_URL)
    soup = BeautifulSoup(req.text, features="html.parser")

    power_generation_table = soup.find(class_="power-generation")
    power_generation_df = pd.read_html(io.StringIO(str(power_generation_table)))[0]

    current_time = soup.findAll(class_="power-generation")[1].find(class_='pgen-date').get_text()
    current_time = current_time[len('(as at) '):]
    print(f'Scraping Generation Data ({current_time})')
    # print(current_time)

    island = ''
    output_row = [current_time]
    for row in power_generation_table.findAll('tr'):
        # print(row)
        if row['class'][0] == 'subheading':
            island = list(row.stripped_strings)[0]
        else:
            generation_type = row.find(class_='name').text
            generation = row.find(class_='generation').text
            output_row.append(generation)

    with open('PowerGeneration.csv', 'a+', encoding='utf-8', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(output_row)

    return datetime.strptime(current_time, '%d %b %Y %H:%M')


if __name__ == '__main__':
    scrape_generation_data()
