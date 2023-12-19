import logging
import sys

from waveshare_epd import epd7in5_V2

if sys.platform == 'win32':
    DEBUG = True
else:
    DEBUG = False

logging.basicConfig(level=logging.DEBUG)

pil_logger = logging.getLogger('PIL')
pil_logger.setLevel(logging.INFO)


class ePaper:
    def __init__(self):
        self.epd = epd7in5_V2.EPD()
        self.epd.init()
        self.epd.Clear()

        self.log = logging.getLogger('ePaper')

    def refresh(self, image_path):
        self.log.info("refreshing ePaper")
        try:
            self.log.info("displaying image")
            self.epd.display(self.epd.getbuffer(image_path))
        except Exception as e:
            self.log.error(e)

    def close(self):
        epd7in5_V2.epdconfig.module_exit()


if __name__ == "__main__":
    e_paper = ePaper()
    e_paper.refresh()
