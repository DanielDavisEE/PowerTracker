import pygame, os, connWiFi, platform, csv, datetime
import matplotlib.pyplot as plt
import numpy as np
from pygame.locals import *
import UpdateData, CreateGraph
from ReversedFile import *

#Fail to create pixmap with Tk_GetPixmap in TkImgPhotoInstanceSetSize

HOUSE = "home"
WIFI_INFO = {
    "flat": {"name": "DoBro Stinson",
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
        
        window.fill(WHITE)
        
        graph = pygame.image.load("PowerPlot.png")
        graphrect = graph.get_rect()   
        window.blit(graph, graphrect)
            
        for i, img_name in enumerate(os.listdir('Icons')):
            
            # Generation Block
            coords = (int(((WIN_WIDTH - graphrect.right) // 2) * (i // 4) + graphrect.right), 
                      int((WIN_HEIGHT // 4) * (i % 4)))
            dimensions = (int((WIN_WIDTH - graphrect.right) // 2),
                          int(WIN_HEIGHT // 4))
            block = pygame.Surface(dimensions)
            block = block.convert()
            block.fill(WHITE)
            
            # Generation Icon
            icon = pygame.image.load("Icons\\" + img_name)
            icon_rect = icon.get_rect()
            
            # Generation Value
            gen_type = img_name.removesuffix('.png')[3:]
            if gen_type in ('Wind', 'Hydro'):
                mw_generation = (float(latest_gen_data['NI' + gen_type])#.removesuffix(' MW'))
                                + float(latest_gen_data['SI' + gen_type]))#.removesuffix(' MW')))
            else:
                mw_generation = float(latest_gen_data[gen_type])#.removesuffix(' MW'))
                
            fraction_generation = mw_generation * 100 / total_generation
    
            font = pygame.font.Font('Humor-Sans-1.0.ttf', 38)
            centre_coords = [int(n // 2) for n in dimensions]
            
            text = font.render(f'{fraction_generation:.1f}%', 1, BLACK)
            text_rect = (text.get_rect(right=dimensions[0] - 10,
                                       centery=centre_coords[1]))          
                    
            block.blit(icon, icon_rect)
            block.blit(text, text_rect)
            
            window.blit(block, coords)
    
            
        loop_count += 1         
        pygame.display.flip()  
        
    pygame.quit()


if __name__ == "__main__":
    window = init_powerTracker()
    run_powerTracker(window)