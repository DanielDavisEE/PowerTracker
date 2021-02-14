import os, connWiFi, platform, csv, datetime, time
import UpdateData, CreateGraph
from ReversedFile import *

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
        self.loop_count = 1
        self.running = False
        
        for event_period in self.loop_event_dict.keys():
            assert event_period % self.period == 0
        
    def run(self):
        self.running = True
        while self.running:
            time.sleep(self.period)
            for period, event in self.loop_event_dict.items():
                if self.loop_count % period == 0:
                    event()
                    
            self.loop_count += 1
        print("LOOP ENDED")
            
    def add_event(self, period, event):
        assert type(period) is int
        self.loop_event_dict[period] = event
        
    def halt(self):
        self.running = False

if __name__ == "__main__":
    
    loop_events = {
        1: lambda : print('loop')
        #10: runGUI,
        #60 * 5: scrapeData,
        #60 * 60 * 24: updateCode
    }
    mainloop = Loop(1, loop_events)
    
    def restart_and_close():
        mainloop.halt()
        os.system("git pull origin main")
        time.sleep(10)
        with open("PowerTrackerGUI.py") as f:
            exec(f.read())
    
    mainloop.add_event(10, restart_and_close)
    
    mainloop.run()