import csv
import datetime
import logging
import os
import sys
import time
from collections import namedtuple

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

LoopEvent = namedtuple("LoopEvent", ["function", "period"])
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
def updateData():
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


@print_name
def refreshCode():
    return_val = CheckAndUpdateFiles()
    if return_val == 'upgraded':
        logging.info('pull from repository')
        cmds = [sys.executable, 'PowerTrackerGUI.py']
        os.execv(cmds[0], cmds)
    elif return_val == 'same':
        logging.info('files already up-to-date')
    else:
        print(return_val)


class Loop():
    def __init__(self, period, init_functions=None, halt_functions=None):
        """
         - period: the loop period in seconds
        """
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
                for period, events in self.loop_event_dict.items():
                    if self.loop_count % (period // self.period) == 0:
                        for event in events:
                            event()

                self.loop_count += 1

            except KeyboardInterrupt:
                logging.info("ctrl + c:")
                self.halt()

        print("LOOP ENDED")

    def add_event(self, event):
        assert event.period % self.period == 0
        self.loop_event_dict[event.period] = self.loop_event_dict.get(event.period, [])
        self.loop_event_dict[event.period].append(event.function)

    def add_events(self, loop_events):
        for event in loop_events:
            self.add_event(event)

    def halt(self):
        self.running = False
        for f in self.halt_functions:
            f()


if __name__ == "__main__":
    minute = 60  # s
    mainloop = Loop(period=minute,
                    init_functions=[ePaperGUI.init_ePaper],
                    halt_functions=[ePaperGUI.exit_ePaper])

    mainloop_events = {
        LoopEvent(updateData, 5 * minute),
        LoopEvent(refreshCode, 30 * minute)
    }
    mainloop.add_events(mainloop_events)
    mainloop.run()
