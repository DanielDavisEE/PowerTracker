import pygame, os, connWiFi, platform, csv, datetime, ePaperGUI
import matplotlib.pyplot as plt
import numpy as np
from pygame.locals import *
import UpdateData, CreateGraph
from ReversedFile import *


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

def updateData():
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
    
    ePaperGUI.refresh_ePaper

class Loop():
    def __init__(self, period, init_functions=None):
        if init_functions is None:
            init_functions = []
        
        self.period = period
        self.loop_event_dict = {}
        self.loop_count = 0
        self.running = False
        
        for f in init_functions:
            f()
        
    def run(self):
        self.running = True
        while self.running:
            time.sleep(self.period)
            for period, event in self.loop_event_dict.items():
                if self.loop_count % period == 0:
                    event()
                    
            self.loop_count += 1
            
    def add_event(self, period, event):
        self.loop_event_dict[period] = event
        
    def halt(self):
        self.running = False

if __name__ == "__main__":
    mainloop = Loop(period=10, init_functions=[ePaperGUI.init_ePaper])
    
    def refreshCode():
        mainloop.halt()
        os.system("git pull origin main")
        time.sleep(10)
        os.system('PowerTrackerGUI.py')
        #with open("PowerTrackerGUI.py") as f:
            #exec(f.read())
    
    loop_events = {
        1: updateData,
        10: refreshCode,
    }