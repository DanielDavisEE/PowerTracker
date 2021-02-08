import time, requests, os, json
from bs4 import BeautifulSoup

url = 'https://www.transpower.co.nz/power-system-live-data'
illegal_characters = ['\\', '/', ':', '*', '"', '?', '<', '>', '|']


def scrape_data():
    with open('generation_data.json', 'r') as infile:
        generation_dict = json.load(infile)
    
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="html.parser")
    
    power_generation_table = soup.find_all(class_="power-generation")[1].table.tbody
    #print(power_generation_table)
    #print(power_generation_table.contents)
    
    island = ''
    for row in power_generation_table.findAll('tr'):
        print(row)
        if row['class'][0] == 'subheading':
            island = list(row.stripped_strings)[0]
        else:
            generation_type = row.find(class_='name').text
            generation = row.find(class_='generation').text + ' MW'
            generation_dict[island][generation_type]['Generation'] = generation
            print(island, generation_type, generation)
        
    with open('generation_data.json', 'w') as outfile:
        json.dump(generation_dict, outfile, indent=4)
        
        
if __name__ == '__main__':
    scrape_data()