import json
import os
import subprocess
import sys
from datetime import datetime
import requests


def CheckAndUpdateFiles():
    # if platform.system() == "Windows":
    #     import requests
    #
    #     git_metadata_str = requests.get("https://api.github.com/repos/DanielDavisEE/PowerTracker/commits/main").text
    # elif platform.system() == "Linux":
    #     git_metadata_str = subprocess.run(
    #         "curl https://api.github.com/repos/DanielDavisEE/PowerTracker/commits/main",
    #         shell=True,
    #         capture_output=True,
    #         encoding='utf-8')
    # else:
    #     raise Exception

    git_metadata_str = requests.get("https://api.github.com/repos/DanielDavisEE/PowerTracker/commits/main").text
    date_str = json.loads(git_metadata_str)['commit']['author']['date']
    new_date = datetime.fromisoformat(date_str[:-1])

    try:
        with open('metadata/timestamp', 'r', encoding='utf-8') as timestamp:
            current_date = datetime.fromisoformat(timestamp.read())
    except FileNotFoundError:
        current_date = datetime.min
        with open('metadata/timestamp', 'w', encoding='utf-8') as timestamp:
            timestamp.write(datetime.isoformat(current_date))

    if current_date < new_date:
        # There has been a more recent commit
        try:
            subprocess.run('git pull', shell=True, check=True)
        except subprocess.CalledProcessError as e:
            return e
        else:
            # TODO Have this file run by cron and close the current process

            # subprocess.run('ps aux | grep "PowerTrackerGUI"',
            #                shell=True,
            #                capture_output=True,
            #                encoding='utf-8')
            return 'upgraded'
    else:
        return 'same'
