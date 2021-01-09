#!/usr/bin/env python3
from os import cpu_count
import matplotlib
from matplotlib import pyplot as plt
import json
import datetime as dt
from datetime import datetime
import numpy as np

LOG_FILE='test2.log'

matplotlib.use('TkAgg')

resources_cpu = {}
resources_mem = {}

parallel_num = 0
parallel_record = {}

app_infos = {}

def get_app_infos():
    global parallel_num
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if 'NfvApp' in line:
                line_part = line.split(' ')
                name, start_time, duration_time = line_part[1], line_part[2], line_part[3]
                app_infos[name] = [start_time, duration_time]
    print(app_infos)

def get_app_nums():
    global parallel_num
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if 'upload_config' in line or 'remove_config' in line:
                line_part = line.split(' ')
                time = line_part[2]
                if 'upload_config' in line:
                    parallel_num = parallel_num + 1
                else:
                    parallel_num = parallel_num - 1
                parallel_record[time] = parallel_num
    print(parallel_record)


def get_resources():
    global resources
    with open(LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if 'resources' in line:
                # print(line)
                line_part = line.split(' ')
                time, result = line_part[2], line_part[3]
                result_cpu = json.loads(result)['used']['CPU']
                result_mem = json.loads(result)['used']['MEM']
                resources_cpu[time] = int(result_cpu ) / 10000
                resources_mem[time] = int(result_mem) / 1000000
    # print(resources_cpu)
    # print(resources_mem)

def do_plot():
    global resources
    my_day = dt.date(2014, 7, 15)
    start_time = datetime.combine(my_day, datetime.strptime(list(resources_cpu.keys())[0], '%H:%M:%S').time())

    xs = [datetime.combine(my_day, datetime.strptime(d, '%H:%M:%S').time()) for d in resources_cpu.keys()]

    xs = [(t - start_time).seconds for t in xs]
    # print(xs)

    plt.figure(1)

    ax1 = plt.subplot(2, 1, 2)

    # print (xs, list(resources_cpu.values()))
    # print (xs, list(resources_mem.values()))
    
    lns1 = ax1.plot(xs, list(resources_cpu.values()), 'o-k', label='CPU Usage (%)')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('CPU Usage (%)')
    ax1.grid()

    ax2 = ax1.twinx()
    lns2 = plt.plot(xs, list(resources_mem.values()), 'x-k', label='RAM (MB)')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('RAM (MB)')

    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=0)

    xs2 = [datetime.combine(my_day, datetime.strptime(d, '%H:%M:%S').time()) for d in parallel_record.keys()]
    xs2 = [(t - start_time).seconds for t in xs2]

    apps = list(app_infos.keys())
    y_pos = np.arange(len(apps))
    start_x = []
    duration_x = []
    first_app_start = int(float(list(app_infos.values())[0][0]))
    for info in app_infos.values():
        start_x.append(int(float(info[0])) - first_app_start)
        duration_x.append(int(float(info[0])) - first_app_start + int(info[1]))

    start_x, duration_x = np.array(start_x), np.array(duration_x)
    print(start_x, duration_x)


    ax3 = plt.subplot(2, 1, 1, sharex=ax1)
    ax3.set_title('CPU and MEM status')
    # ax4.barh(y_pos, start_x, color='green')
    ax3.barh(y_pos, duration_x, left=start_x, color='0.5', height=0.3)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(apps)
    ax3.set_ylabel('App name')

    ax4 = ax3.twinx()
    ax4.plot(xs2, list(parallel_record.values()), 'o-k')
    ax4.set_xlabel('Time')
    ax4.set_ylabel('App nums')
    ax4.grid()

    plt.show()
    

if __name__ == '__main__':
    get_app_infos()
    print(app_infos)
    get_app_nums()
    print(parallel_record)
    get_resources()
    print(resources_cpu)
    do_plot()
