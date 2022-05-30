import csv
import datetime
import logging
import os
import sys
import time
import math
from collections import namedtuple
from collections.abc import Iterable, Callable

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


# TODO Move this functionality to UpdateFiles.py
@print_name
def refreshCode():
    return_val = CheckAndUpdateFiles()
    if return_val == 'upgraded':
        logging.info('pulled from repository')
        mainloop.halt()
        cmds = [sys.executable, 'PowerTrackerGUI.py']
        os.execv(cmds[0], cmds)
    elif return_val == 'same':
        logging.info('files already up-to-date')
    else:
        print(return_val)


class Loop(dict):
    def __init__(self, *, events: Iterable[LoopEvent],
                 init_functions: Iterable = None, halt_functions: Iterable = None):
        """

        Args:
            events: a dictionary of loop events. The keys are event periods and the lists are the events to
                    be triggered one those periods.
            init_functions: a list of events to be called before the loop starts running.
            halt_functions: a list of events to be called after the loop halts.
        """
        super().__init__()

        if init_functions is None:
            init_functions = []
        if halt_functions is None:
            halt_functions = []
        self.init_functions = init_functions
        self.halt_functions = halt_functions

        self._period = 60
        self._loop_count = 0
        self._running = False
        self.add_events(events)

        event_periods = self.keys()
        self._period = math.gcd(*event_periods)

    @staticmethod
    def _revise_period(f):
        def inner(self, *args, **kwargs):
            f(*args, **kwargs)

            event_periods = self.keys()
            self._period = math.gcd(*event_periods)

        return inner

    def _loop(self):
        for period, events in self.items():
            if (self._loop_count * self._period) % period == 0:
                for event in events:
                    event()
        self._loop_count += 1

    def run(self):
        for f in self.init_functions:
            f()

        self._running = True
        while self._running:
            try:
                time.sleep(self._period)
                self._loop()

            except KeyboardInterrupt:
                logging.info("ctrl + c:")
                self.halt()

        print("LOOP ENDED")

    @_revise_period
    def add_event(self, event):
        if not isinstance(event, LoopEvent):
            event = LoopEvent(**event)
        assert event.period % self._period == 0
        self[event.period] = self.get(event.period, [])
        self[event.period].append(event.function)

    def add_events(self, loop_events):
        for event in loop_events:
            self.add_event(event)

    def halt(self):
        self._running = False
        for f in self.halt_functions:
            f()


if __name__ == "__main__":
    MINUTE = 60  # s
    mainloop_events = {
        LoopEvent(updateData, 5 * MINUTE),
    }
    mainloop = Loop(events=mainloop_events,
                    init_functions=[ePaperGUI.init_ePaper],
                    halt_functions=[ePaperGUI.exit_ePaper])
    mainloop.run()
