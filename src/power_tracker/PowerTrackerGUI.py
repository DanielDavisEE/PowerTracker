import csv
import datetime
import logging
import os
import sys
import time
import math
from collections import namedtuple
from apscheduler.schedulers.blocking import BlockingScheduler

import CreateGraph
import UpdateData
import ePaperGUI
from ReversedFile import ReversedFile
from Utilities import print_name
from UpdateFiles import CheckAndUpdateFiles

logging.basicConfig(level=logging.DEBUG)

plt_logger = logging.getLogger('matplotlib')
plt_logger.setLevel(logging.INFO)

sel_logger = logging.getLogger('selenium')
sel_logger.setLevel(logging.INFO)

req_logger = logging.getLogger('urllib3')
req_logger.setLevel(logging.INFO)

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


@print_name
def main():
    try:
        UpdateData.scrapeLoadData()
        UpdateData.scrapeGenDataReq()
    except:
        print(f"Error collecting data at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")

    logging.info('creating graph')
    CreateGraph.create_graph()

    with open('PowerGeneration.csv', 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(ReversedFile(infile), GEN_TYPES)
        latest_gen_data = reader.__next__()

    total_generation = sum(int(v.removesuffix(' MW')) for k, v in latest_gen_data.items() if k != 'DateTime')

    logging.info('refreshing screen')
    ePaperGUI.refresh_ePaper(latest_gen_data, total_generation)


# TODO Move this functionality to UpdateFiles.py
@print_name
def refreshCode():
    return_val = CheckAndUpdateFiles()
    if return_val == 'upgraded':
        logging.info('pulled from repository')
        scheduler.shutdown()
        cmds = [sys.executable, 'PowerTrackerGUI.py']
        os.execv(cmds[0], cmds)
    elif return_val == 'same':
        logging.info('files already up-to-date')
    else:
        print(return_val)


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'cron', minutes='*/5', id='main_task')
    scheduler.start()
