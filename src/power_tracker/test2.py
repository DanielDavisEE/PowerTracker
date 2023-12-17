import sys
import time

while True:
    print("Hello")
    print(sys.argv)
    for i in range(10, 0, -1):
        print(i)
        time.sleep(1)
