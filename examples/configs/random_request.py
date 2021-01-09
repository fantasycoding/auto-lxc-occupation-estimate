import random
import numpy as np
import threading
import time
import requests
import os
import shelve

debug = False
server = "192.168.31.14"

def get_time():
    return time.strftime("%H:%M:%S", time.localtime())

class NfvApp(threading.Thread):
    def __init__(self, name, start_time, duration):
        threading.Thread.__init__(self)
        self.name = name
        self.start_time = start_time
        self.duration = duration
        print("NfvApp {} {} {}".format(name, start_time, duration))

    def get_resources(self):
        if debug:
            print("http://localhost:8083/1.0/resources/{}".format(server))
        else:
            r = requests.get("http://localhost:8083/1.0/resources/{}".format(server))
            print("{} resources {} {}".format(self.name, get_time(), r.text))
    
    def remove_config(self):
        if debug:
            print("http://localhost:8083/1.0/config/{}".format(self.name))
        else:
            r = requests.delete("http://localhost:8083/1.0/config/{}".format(self.name))
            print("{} remove_config {} {}".format(self.name, get_time(), r.text))

    def is_free(self):
        if debug:
            print("http://localhost:8083/1.0/action/status/{}".format(self.name))
            return True
        else:
            r = requests.get("http://localhost:8083/1.0/action/status/{}".format(self.name))
#             print(r.text.strip(), r.text.strip() == "0")
        return r.text.strip() == "0"

    def wait_do(self, action):
        time.sleep(5)
        while self.is_free() is False:
            time.sleep(5)
        if action == "remove_config":
            self.remove_config()
        else:
            self.control(action)

    def upload_config(self):
        payload = ""
        with open(self.name + ".json", 'r') as f:
            payload = f.read()

        if debug:
            print("http://localhost:8083/1.0/config/{}".format(self.name))
        else:
            r = requests.post("http://localhost:8083/1.0/config/{}".format(self.name), headers={"Content-Type": "application/xml"}, data=payload)
            print("{} upload_config {} {}".format(self.name, get_time(), r.text))

    def control(self, action):
        if debug:
            print("http://localhost:8083/1.0/action/{}/{}".format(action, self.name))
        else:
            r = requests.get("http://localhost:8083/1.0/action/{}/{}".format(action, self.name))
            print("{} {} {} {}".format(self.name, action, get_time(), r.text))

    def run(self):
        time.sleep(self.start_time)
        print("Preparing {}".format(self.name))
        self.upload_config()
        self.control("create")
        self.get_resources()
        print("Starting {}".format(self.name))
        self.wait_do("start")
        self.get_resources()
        time.sleep(self.duration)
        print("Stoping {}".format(self.name))
        self.wait_do("stop")
        self.get_resources()
        print("Destroying {}".format(self.name))
        self.wait_do("destroy")
        self.wait_do("remove_config")
        self.get_resources()
        print("Exiting {}".format(self.name))


arrival_rate = 30

def genTestset():
    apps = ['cn{}'.format(i + 1) for i in range(0, arrival_rate)]
    random.shuffle(apps)

    experimental_total_time = 30 * 60

    arrive_times = []
    t = 0
    for i in range(arrival_rate):
        t += random.expovariate(arrival_rate)
        arrive_times.append(t)

    times = [t * experimental_total_time for t in arrive_times]
    # print(arrive_times)
    durations = np.random.poisson(experimental_total_time / arrival_rate, arrival_rate)
    return apps, times, durations

testset_file = "random_request.txt"

if os.path.exists(testset_file):
    with shelve.open(testset_file) as db:
        experimental_apps = db['apps']
        experimental_times = db['times']
        experimental_durations = db['durations']
else:
    experimental_apps, experimental_times, experimental_durations = genTestset()
    with shelve.open(testset_file) as db:
        db['apps'] = experimental_apps
        db['times'] = experimental_times
        db['durations'] = experimental_durations

for i in range(arrival_rate):
    NfvApp(experimental_apps[i], experimental_times[i], experimental_durations[i]).start()

# NfvApp("tn1", 0, 60).start()