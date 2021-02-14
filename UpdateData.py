import time, requests, os, json, csv, random
from bs4 import BeautifulSoup
from ReversedFile import *
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True

illegal_characters = ['\\', '/', ':', '*', '"', '?', '<', '>', '|']


def clearData():
    for file in os.listdir('PowerData'):
        with open('PowerData\\' + file, 'w') as outfile:
            pass
        
    with open('generation_data.json', 'w') as outfile:
        pass
        
    with open(f'PowerGeneration.csv', 'w', newline='') as outfile:
        pass


def missingTimeSteps(prev_time, curr_time):
    prev_time_dt = datetime.strptime(prev_time, '%d %b %Y %H:%M')
    curr_time_dt = datetime.strptime(curr_time, '%d %b %Y %H:%M')
    time_offset = int(curr_time_dt.timestamp() - prev_time_dt.timestamp())
    assert time_offset % (60 * 5) == 0
    return time_offset // (60 * 5) - 1
        

def scrapeLoadData():
    """ Scrape the load data for each district
    """
    
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.transpower.co.nz/system-operator/operational-information/zone-load-table')
    
    time.sleep(1)
    
    #parent = driver.find_element_by_xpath('//div[@class="panel-pane pane-zone-load-table"]')
    current_time = driver.find_element_by_xpath('//div[@class="live-data-date"]/time').text
    table = driver.find_element_by_xpath('//div[@class="zone-load-table"]/child::*[1]/table/tbody')
    
    print(f'Scraping Load Data ({current_time})')
    table = [x.rsplit(' ', maxsplit=7) for x in table.text.split('\n')[2:]]
    
    driver.quit()
    
    
    for row in table:
        row[0] = row[0].split(' ', maxsplit=1)[-1]
        zone = row[0]
        row[0] = current_time
        #print(zone, row)
        with open(f'PowerData\{zone}.csv', 'a+', newline='') as outfile:
            reader = csv.reader(ReversedFile(outfile))
            try:
                last_data_point = reader.__next__()
            except StopIteration: # The data file is empty
                missed_data_points = 6
            else:
                missed_data_points = missingTimeSteps(last_data_point[0], current_time)
                if missed_data_points < 0:
                    continue
            
            if missed_data_points >= 0:
                dt_current_time = datetime.strptime(current_time, '%d %b %Y %H:%M')
                dt_current_time -= timedelta(minutes=max(5*missed_data_points, 6))
                
                writer = csv.writer(outfile, lineterminator='\n')
                if missed_data_points >= 6:
                    writer.writerows([[''] * 8] * (missed_data_points - 6 + 1))
                    
                tmp_row = row.copy()
                for data_point in range(max(0, 6 - missed_data_points), 6):
                    tmp_row[0] = dt_current_time.strftime('%d %b %Y %H:%M')
                    writer.writerow([dt_current_time.strftime('%d %b %Y %H:%M')] 
                                    + tmp_row[7 - data_point:] 
                                    + [''] * (7 - data_point))
                    print(f"""Extrapolating: {[dt_current_time.strftime('%d %b %Y %H:%M')]
                          + tmp_row[7 - data_point:] 
                          + [''] * (7 - data_point)}""")
                    dt_current_time += timedelta(minutes=5)
                    
                
                writer.writerow(row)
                


def scrapeGenerationData():
    """ Scrape the generation capacity and output datafrom the interactive graph
    """
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.transpower.co.nz/system-operator/operational-information/generation')
    
    time.sleep(1)
    
    Current_Generation = {
        'North Island': {
            'Wind': None,
            'Hydro': None,
            'Geothermal': None,
            'Gas/Coal': None,
            'Gas': None,
            'Diesel/Oil': None,
            'Co-Gen': None,
            
        },
        'South Island': {
            'Wind': None,
            'Hydro': None,
        }
    }
    
    def scroll_shim(html_object):
        """ Function to scroll to html element
        """
        f_driver = driver
        x = html_object.location['x']
        y = html_object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
                x,
                y
            )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        f_driver.execute_script(scroll_by_coord)
        f_driver.execute_script(scroll_nav_out_of_way)
    
    
    ActionChains(driver)
    graph = driver.find_element_by_xpath('//div[@id="highcharts-0"]')
    databars = graph.find_elements_by_xpath('./child::*[1]/*[@class="highcharts-series-group"]/child::*[3]/child::*')
    popup = graph.find_element_by_xpath('./*[@class="highcharts-tooltip"]')
    current_time = driver.find_element_by_xpath('//span[@class="pgen-date"]').text.removeprefix('(as at) ')

    print(f'Scraping Generation Data ({current_time})')    
    
    scroll_shim(graph)
    ActionChains(driver).move_to_element(databars[0]).pause(0.5).perform()
    width = databars[0].get_attribute('width')
    island = 'North Island'
    generation = [current_time]
    
    for databar in databars:
        
        hover_data = popup.find_element_by_xpath('.//tbody')
        gen_type = hover_data.find_element_by_xpath('./tr[1]/td').text
        capacity = hover_data.find_element_by_xpath('./tr[2]/td[2]').text
        generating = hover_data.find_element_by_xpath('./tr[3]/td[2]').text
        generation.append(generating)
        
        if gen_type == 'Co-Gen':
            island = 'South Island'
            
        Current_Generation[island][gen_type] = capacity
        
        ActionChains(driver).move_by_offset(width, 0).pause(0.5).perform()
    
    driver.quit()
    
    with open('generation_data.json', 'w') as outfile:
        json.dump(Current_Generation, outfile, indent=4)
        
    with open(f'PowerGeneration.csv', 'a+', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(generation)


def scrapeGenDataSel():
    """ Scrape the load and generation output data for new zealand
    """
    driver = webdriver.Firefox(options=options)
    driver.get('https://www.transpower.co.nz/power-system-live-data')
    
    time.sleep(1)
    
    soup = BeautifulSoup(driver.page_source, features="html.parser")
    driver.quit()
    power_gen_table = soup.findAll(class_="power-generation")[1].table.tbody
    current_time = soup.findAll(class_="power-generation")[1].find(class_='pgen-date').get_text()
    current_time = current_time[len('(as at) '):]
    print(f'Scraping Generation Data ({current_time})')   
    #print(current_time)
    island = ''
    output_row = [current_time]
    for row in power_gen_table.findAll('tr'):
        #print(row)
        if row['class'][0] == 'subheading':
            island = list(row.stripped_strings)[0]
        else:
            generation_type = row.find(class_='name').text
            generation = row.find(class_='generation').text
            output_row.append(generation)
        
    #print(output_row)
    #with open(f'PowerGeneration.csv', 'a+', newline='') as outfile:
        #writer = csv.writer(outfile)
        #writer.writerow(output_row)
    return datetime.strptime(current_time, '%d %b %Y %H:%M')
    
    
def scrapeGenDataReq():
    #with open('generation_data.json', 'r') as infile:
        #generation_dict = json.load(infile)
    
    req = requests.get('https://www.transpower.co.nz/power-system-live-data')
    soup = BeautifulSoup(req.text, features="html.parser")
    
    #print(soup.find_all(class_="power-generation"))
    power_generation_table = soup.find_all(class_="power-generation")[1].table.tbody

    current_time = soup.findAll(class_="power-generation")[1].find(class_='pgen-date').get_text()
    current_time = current_time[len('(as at) '):]
    print(f'Scraping Generation Data ({current_time})')   
    #print(current_time)
    
    island = ''
    output_row = [current_time]
    for row in power_generation_table.findAll('tr'):
        #print(row)
        if row['class'][0] == 'subheading':
            island = list(row.stripped_strings)[0]
        else:
            generation_type = row.find(class_='name').text
            generation = row.find(class_='generation').text
            output_row.append(generation)
        
    with open(f'PowerGeneration.csv', 'a+', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(output_row)
    
    return datetime.strptime(current_time, '%d %b %Y %H:%M')        
        
if __name__ == '__main__':

    scrapeLoadData()