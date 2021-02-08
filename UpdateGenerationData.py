import time, requests, os, json, csv
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options

options = Options()
options.headless = True
MOZ_HEADLESS=1


def scrape_data():
    driver = webdriver.Firefox()
    driver.get('https://www.transpower.co.nz/system-operator/operational-information/generation')
    
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
    current_time = graph.find_element_by_xpath('./span[@class="pgen-date"]').text.removeprefix('(as at) ')
    
    
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
            
        Current_Generation[island][gen_type] = {
            'Capacity': capacity,
            'Generating': generating
        }
        
        ActionChains(driver).move_by_offset(width, 0).pause(0.5).perform()
    
    driver.quit()
    
    with open('generation_data.json', 'w') as outfile:
        json.dump(Current_Generation, outfile, indent=4)
        
    with open(f'PowerGeneration.csv', 'a+', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(generation)

if __name__ == '__main__':
    scrape_data()