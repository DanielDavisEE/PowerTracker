import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

start_time = time.time()


def hello():
    print(f"{datetime.now().timestamp()}: {time.time() - start_time} seconds since start")
    time.sleep(5)


# datetime.timestamp()
scheduler = BlockingScheduler()
scheduler.add_job(hello, 'cron', second='*/10')
scheduler.start()
