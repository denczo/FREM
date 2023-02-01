import psutil
import time


def cpu_load(interval=1):
    startTime = time.time()
    endTime = 0

start_time = time.time()
endTime = 0
elapsedTime = 0
interval = 1


import sys


def progress(count, total, status=''):
    bar_len = 20
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '|' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))

    # sys.stdout.write('[%s] %s%s %s\r' % (bar, percents, '%', status))
    # sys.stdout.flush()

cpu_count = psutil.cpu_count(True)

while True:
    cpu_loads = psutil.cpu_percent(interval=1, percpu=True)
    for cpu_load in cpu_loads:
        progress(cpu_load, 100)
    sys.stdout.flush()

    # if elapsedTime >= interval:
        # print ('\r[{0}] {1}%'.format('#'*(100/10), 100))
        #print("\rProgress: [{0:50s}] {1:.1f}%".format('#' * int(4 * 50), 4 * 100), end="", flush=True)
        #print("\rCPU LOAD", psutil.cpu_percent(interval=1, percpu=True))
        # print("CPU FREQ", psutil.cpu_freq())
        # start_time = time.time()
    # elapsedTime = time.time() - start_time

#htop in linux for percentage cpu
