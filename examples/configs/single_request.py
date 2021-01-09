import random
import numpy as np
import threading
import time
import requests
import os
import shelve

debug = False
servers = ["192.168.31.13", "192.168.31.14", "192.168.31.15"]

def get_time():
    return time.strftime("%H:%M:%S", time.localtime())

class NfvApp(threading.Thread):
    def __init__(self, name, start_time, duration):
        threading.Thread.__init__(self)
        self.name = name
        self.start_time = start_time
        self.duration = duration
        self.ok = True
        print("NfvApp {} {} {}".format(name, start_time, duration))

    def get_resources(self):
        for server in servers:
            if debug:
                print("http://localhost:8083/1.0/resources/{}".format(server))
            else:
                r = requests.get("http://localhost:8083/1.0/resources/{}".format(server))
                print("{} resources {} {}".format(self.name, get_time(), r.text))

    def get_position(self):
        for server in servers:
            if debug:
                print("http://localhost:8083/1.0/info/{}".format(self.name))
            else:
                r = requests.get("http://localhost:8083/1.0/info/{}".format(self.name))
                print("{} info {} {}".format(self.name, get_time(), r.text))
        
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

    def is_failed(self):
        if debug:
            print("http://localhost:8083/1.0/action/status/{}".format(self.name))
            return True
        else:
            r = requests.get("http://localhost:8083/1.0/action/status/{}".format(self.name))
#             print(r.text.strip(), r.text.strip() == "0")
        return r.text.strip() == "2"

    def wait_do(self, action):
        if action == "remove_config":
            while self.is_failed() is False and self.is_free() is False:
                time.sleep(5)
            self.remove_config()
            return
        if self.ok is False:
            return
        time.sleep(1)
        while self.is_free() is False:
            if self.is_failed():
                self.ok = False
                print("{} {} Failed".format(self.name, action))
                return
            time.sleep(1)
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
        self.get_position()
        # time.sleep(self.duration)
        # print("Stoping {}".format(self.name))
        # self.wait_do("stop")
        # self.get_resources()
        # print("Destroying {}".format(self.name))
        # self.wait_do("destroy")
        # self.wait_do("remove_config")
        # self.get_resources()
        # print("Exiting {}".format(self.name))

NfvApp("cn360", 0, 60).start()
