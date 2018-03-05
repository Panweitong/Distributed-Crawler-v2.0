import inspect
import time
import json
import socket
import wmi
import os
import win32con
import win32api
import urllib.request

class mon:


    def __init__(self):
        self.data = {}

    def getTime(self):
        return str(int(time.time()) + 8 * 3600)

    def getHost(self):
        return socket.gethostname()

    def getMemTotal(self):
        c = wmi.WMI()
        for sys in c.Win32_OperatingSystem():
            return sys.TotalVisibleMemorySize

    def getMemUsage(self):
        c = wmi.WMI()
        for sys in c.Win32_OperatingSystem():
            total = sys.TotalVisibleMemorySize
            free = sys.FreePhysicalMemory
            usage = int(total)-int(free)
            #print()
            return str(usage)

    def getMemFree(self):
        c = wmi.WMI()
        for sys in c.Win32_OperatingSystem():
            return sys.FreePhysicalMemory

    def runAllGet(self):
        for fun in inspect.getmembers(self,predicate=inspect.ismethod):
        #for fun in [getTime,getHost,getMemtotal,getMemUsage,getMemFree]:
            #print(fun[:3])
            if fun[0][:3] == 'get':
                #print(fun[:3])
                self.data[fun[0][3:]] = fun[1]()
                #print(self.data)
        return self.data

if __name__ == "__main__":
    while True:
        m = mon()
        values = m.runAllGet()
        print(values)
        #data = urllib.parse.urlencode(values).encode('utf-8')
        #print(data)
        data = json.dumps(values)
        data = bytes(data,'utf-8')      #改变数据类型为bytes，不然在urlopen时无法传递数据
        #print(data)

        req = urllib.request.Request("http://127.0.0.1:5000/mon",data,{'Content-Type': 'application/json'})

        print(req)
        try:
            f = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:

            print(e.code)
            print(e.read().decode())
        #f = urllib.parse.urlencode(b'req')
        response=f.read()
        print(response)
        f.close()
        time.sleep(2)