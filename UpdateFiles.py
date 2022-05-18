import subprocess, platform, json, os, sys
from datetime import datetime

# '%Y-%m-%dT%H:%M:%SZ'
# "2022-05-15T09:20:16Z"
# "curl https://api.github.com/repos/DanielDavisEE/PowerTracker/commits/main 2>&1 | grep '\"date\"' | tail -n 1 | awk '{print $2}'"

if platform.system() == "Windows":
    import requests

    git_metadata_str = requests.get("https://api.github.com/repos/DanielDavisEE/PowerTracker/commits/main").text
elif platform.system() == "Linux":
    git_metadata_str = subprocess.run("curl https://api.github.com/repos/DanielDavisEE/PowerTracker/commits/main",
                                      shell=True,
                                      capture_output=True,
                                      encoding='utf-8')
else:
    raise Exception

date_str = json.loads(git_metadata_str)['commit']['author']['date']
new_date = datetime.fromisoformat(date_str[:-1])

try:
    with open('metadata', 'r', encoding='utf-8') as metadata:
        current_date = datetime.fromisoformat(metadata.read())
except FileNotFoundError:
    current_date = datetime.min
    with open('metadata', 'w', encoding='utf-8') as metadata:
        current_date = datetime.isoformat(current_date)

if current_date < new_date:
    # There has been a more recent commit
    try:
        subprocess.run('git pull', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e)
    os.execv(sys.executable, sys.argv + ['--updated'])
    # subprocess.run('git pull https://github.com/DanielDavisEE/PowerTracker.git@main')
    # subprocess.run([sys.executable, '-m', 'pip', 'install', '-U',
    #                 'git+https://github.com/DanielDavisEE/PowerTracker.git@main'])
    # os.execv(sys.executable, sys.argv + ['--updated'])
