import pygame, os, connWiFi, platform, csv, datetime
import matplotlib.pyplot as plt
import numpy as np
from pygame.locals import *
import UpdateData, CreateGraph
from ReversedFile import *

#Fail to create pixmap with Tk_GetPixmap in TkImgPhotoInstanceSetSize

HOUSE = "flat"
WIFI_INFO = {
    "flat": {"name": "Elizabeth House Wifi",
             "SSID": "Elizabeth House Wifi",
             "key": "setthealarm"},
    "oldflat": {"name": "DoBro Stinson",
                "SSID": "DoBro Stinson",
                "key": "Barney69"},
    "home": {"name": "homebase",
             "SSID": "homebase",
             "key": "tobycat12"},
}
WIN_WIDTH, WIN_HEIGHT = 800, 400
WHITE = 255, 255, 255
BLACK = 0, 0, 0

ROWS, COLUMNS = 4, 2

GEN_TYPES = [
    'DateTime',
    'NIWind',
    'NIHydro',
    'Geothermal',
    'Gas-Coal',
    'Gas',
    'Diesel-Oil',
    'Co-Gen',
    'SIWind',
    'SIHydro'
]

def init_powerTracker():
    
    #connWiFi.createNewConnection(**WIFI_INFO[HOUSE])
    #connWiFi.connect(**WIFI_INFO[HOUSE])
    
    pygame.init()
    pygame.display.set_caption("PowerTracker")
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    
    #UpdateData.clearData()
    
    return window


def run_powerTracker(window):
    # Loop GUI
    period = 10000 # ms
    scrape_period_1 = 1000 * 60 * 5 // period
    scrape_period_2 = 1000 * 60 * 60 * 24 // period
    loop_count = 0
    running = True
    
    while running:
        pygame.time.delay(period)
        
        
        if platform.system() == "Windows":
            for event in pygame.event.get():
                # Keyboard Events
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False # Allows user to overwrite quit process
                    
                if event.type == pygame.QUIT:
                    running = False
        
        
        if loop_count % scrape_period_1 == 0:
            try:
                UpdateData.scrapeLoadData()
                UpdateData.scrapeGenDataReq()
            except:
                print(f"Error collecting data at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
            CreateGraph.create_graph()
        
            with open('PowerGeneration.csv', 'r') as infile:
                reader = csv.DictReader(ReversedFile(infile), GEN_TYPES)
                latest_gen_data = reader.__next__()
                
            total_generation = sum(int(v.removesuffix(' MW')) for k, v in latest_gen_data.items() if k != 'DateTime')
            
        
        if loop_count % scrape_period_2 == 0:
            loop_count = 0
            pass


class Loop():
    def __init__(self, period, loop_events):
        self.period = period
        self.loop_event_dict = loop_events
        self.loop_count = 0
        self.running = False
        
    def run(self):
        self.running = True
        while self.running:
            for period, event in self.loop_event_dict.items():
                if self.loop_count % self.period == 0:
                    event()
                    
            self.loop_count += 1
            
    def add_event(self, period, event):
        self.loop_event_dict[period] = event

if __name__ == "__main__":
    loop_events = {
        10000: runGUI,
        1000 * 60 * 5: scrapeData,
        1000 * 60 * 60 * 24: updateCode
    }
    mainloop = Loop(10000, loop_events)