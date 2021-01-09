import numpy as np
import threading
import time
import requests
import json

debug = False
servers = ["192.168.31.15"]

def get_time():
    return time.strftime("%H:%M:%S", time.localtime())

class Resource(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.record = {}

    def get_resources(self):
        now_time = get_time()
        self.record[now_time] = []
        for server in servers:
            if debug:
                print("http://localhost:8083/1.0/resources/{}".format(server))
            else:
                r = requests.get("http://localhost:8083/1.0/resources/{}".format(server))
                print("{} {} {}".format(server, now_time, r.text))
                self.record[now_time].append(json.loads(r.text)['used']['CPU'] / 10000)


    def run(self):
        for i in range(50):
            self.get_resources()
            time.sleep(5)
        i = 0
        for server in servers:
            data = np.array(list(self.record.values()))[:, i]
            print(server, data.mean())
            i = i + 1
            
            
Resource().start()
