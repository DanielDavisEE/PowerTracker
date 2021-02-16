import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
    
if sys.platform == 'win32':
    DEBUG = True
else:
    DEBUG = False

import logging
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
if DEBUG:
    pass
else:
    from waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.DEBUG)

EPD_WIDTH       = 800
EPD_HEIGHT      = 480
V_MARGIN        = 40

if DEBUG:
    class EPD():
        def __init__(self):
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
            
    latest_gen_data = {
        'DateTime': '3/01/2021 11:46',
        'NIWind': '88',
        'NIHydro': '759',
        'Geothermal': '921',
        'Gas-Coal': '0',
        'Gas': '375',
        'Diesel-Oil': '0',
        'Co-Gen': '157',
        'SIWind': '3',
        'SIHydro': '1880'
    }    
    total_generation = sum(int(v.removesuffix(' MW')) for k, v in latest_gen_data.items() if k != 'DateTime')
    
    
class BBox():
    def __init__(self, image):
        self.left, self.top, self.right, self.bottom = image.getbbox()
        
    def __str__(self):
        return f'Bounding Box(left: {self.left}, right: {self.right}, top: {self.top}, bottom: {self.bottom})'
    
def init_ePaper():
    global epd, font38
    
    font38 = ImageFont.truetype('Humor-Sans.ttf', 38)
    
    if DEBUG:
        epd = EPD()
    else:
        epd = epd7in5_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

def refresh_ePaper():
    
    try:
    
        mainImage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        graphImage = Image.open("PowerPlot.png")
        mainImage.paste(graphImage, (0, V_MARGIN))
        draw_mainImage = ImageDraw.Draw(mainImage)
        
        graphrect = BBox(graphImage)
        icons_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Icons')
        for i, img_name in enumerate(os.listdir(icons_path)):
            pass
            
            # Generation Block
            coords = (int(((epd.width - graphrect.right) // 2) * (i // 4) + graphrect.right), 
                      int(((epd.height - V_MARGIN * 2) // 4) * (i % 4)) + V_MARGIN)
            
            # Generation Icon
            iconImage = Image.open(os.path.join(icons_path, img_name))
            iconBBox = BBox(iconImage)
            mainImage.paste(iconImage, coords)
            
            # Generation Value
            gen_type = img_name.removesuffix('.png')[3:]
            if gen_type in ('Wind', 'Hydro'):
                mw_generation = (float(latest_gen_data['NI' + gen_type])#.removesuffix(' MW'))
                                + float(latest_gen_data['SI' + gen_type]))#.removesuffix(' MW')))
            else:
                mw_generation = float(latest_gen_data[gen_type])#.removesuffix(' MW'))
            fraction_generation = mw_generation * 100 / total_generation
            
            coords_text = (coords[0] + iconBBox.right, coords[1] + iconBBox.bottom // 2)
            
            draw_mainImage.text(coords_text, f'{fraction_generation:.1f}%', anchor="lm", font = font38, fill = 0)
        
        if DEBUG:
            mainImage.save("GUIImage.png")
        else:
            epd.display(epd.getbuffer(mainImage))

    
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        
def exit_ePaper():
    epd7in5_V2.epdconfig.module_exit()
    exit()
    
if __name__ == "__main__":
    init_ePaper()
    refresh_ePaper()