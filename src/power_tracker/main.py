import logging

from e_paper_drivers import ePaper
from graphing import create_image
from web_drivers import scrape_generation_data, save_generation_data

logging.basicConfig(filename='power_tracker.log', level=logging.DEBUG)

ePAPER = ePaper()


def main():
    generation_data = scrape_generation_data()
    save_generation_data(generation_data)
    
    image_path = create_image()
    ePAPER.refresh(image_path)


if __name__ == '__main__':
    main()
