# import ePaperGUI

# ePaperGUI.init_ePaper()
# ePaperGUI.refresh_ePaper(debug=True)
# ePaperGUI.exit_ePaper()
"""

from os.path import getmtime
WATCHED_FILES = os.listdir(os.getcwd())
WATCHED_FILES_MTIMES = [(f, getmtime(f)) for f in WATCHED_FILES]
os.system("git pull origin main")
#help(sys.executable)
for f, mtime in WATCHED_FILES_MTIMES:
    print(f, datetime.utcfromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'))
    if getmtime(f) != mtime:
        pass
        #os.execv(Path(__file__).absolute(), ())
        #os.execv(sys.executable, ['python'] + sys.argv)
"""
# print('Ran')
# os.execv(sys.executable, sys.argv)
# os.execv(sys.executable, ['python'] + sys.argv)
# print('end')
# time.sleep(1)
# def refreshCode():
##mainloop.halt()
##
##time.sleep(10)
##print('Rerun')
# os.system('test1.py')

# print(f"{time.time():.2f}")
##time.sleep(10)   
##print('Pull')
# refreshCode()
##print('End')
# print('test')

import os
import sys

print("Executing...")
os.execl(sys.executable, r'C:\Users\Daniel\OneDrive - University of Canterbury\Other Stuff\Code\PowerTracker\test2.py')
print('Closing.')
