import os, connWiFi, platform, csv, datetime, time
import UpdateData, CreateGraph, ePaperGUI
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
    
    ePaperGUI.refresh_ePaper()

class Loop():
    def __init__(self, period, init_functions=None, halt_functions=None):
        if init_functions is None:
            init_functions = []
        if halt_functions is None:
            halt_functions = []
        self.halt_functions = halt_functions
        
        self.period = period
        self.loop_event_dict = {}
        self.loop_count = 1
        self.running = False
        
        for event_period in self.loop_event_dict.keys():
            assert event_period % self.period == 0
            
        for f in init_functions:
            f()
        
    def run(self):
        self.running = True
        while self.running:
            try:
                time.sleep(self.period)
                for period, event in self.loop_event_dict.items():
                    if self.loop_count % (period // self.period) == 0:
                        event()
                        
                self.loop_count += 1
                
            except KeyboardInterrupt:
                self.halt()
                
        print("LOOP ENDED")
            
    def add_event(self, period, event):
        assert type(period) is int
        self.loop_event_dict[period] = event
        
    def halt(self):
        self.running = False
        for f in self.halt_functions:
            f()

if __name__ == "__main__":
    
    mainloop = Loop(period=10, init_functions=[ePaperGUI.init_ePaper], halt_functions=[ePaperGUI.exit_ePaper])
    
    def refreshCode():
        mainloop.halt()
        os.system("git pull origin main")
        time.sleep(10)
        os.system('PowerTrackerGUI.py')
    
    loop_events = {
        10: updateData,
        60: refreshCode,
    }
