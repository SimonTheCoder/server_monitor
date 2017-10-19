#!/usr/bin/python

coding='UTF8'

__author__="SimonTheCoder"

import sys
import subprocess
import re 
import time
import threading

class Server:
    re_ip_address = re.compile(r'PING [^\(]+\((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)')

    class State:
        SERVER_STATE_UP = 1
        SERVER_STATE_DOWN = -1

        def __init__(self, state, host, ip, time):
            self.state = state
            self.host = host
            self.ip = ip
            self.time = time

        def __str__(self):
            if self.state == self.SERVER_STATE_UP:
                #print "Host: %s(%s) is UP, ping time: %f" % (self.host, self.ip, self.time)
                return "Host: %s(%s) is UP, ping time: %f" % (self.host, self.ip, self.time)
            else:
                return "Host: %s is DOWN" % (self.host)

    def __init__(self, host):
        self.host = host

    def check_state(self):
        try:
            ping_start = time.time()
            ping_result = subprocess.check_output("ping -c 1 %s" % (self.host), shell=True)
            ping_time = time.time() - ping_start
            ip = self.re_ip_address.match(ping_result).group(1)
            ret_state = self.State(self.State.SERVER_STATE_UP, self.host, ip, ping_time)
            self.last_state = ret_state
            return ret_state
        except subprocess.CalledProcessError,e:
            ret_state = self.State(self.State.SERVER_STATE_DOWN, self.host, None, -1)
            self.last_state = ret_state
            return ret_state
        except Exception,e:
            print e
            self.last_state = None
            return None

class Monitor:
    class State:
        NOT_INIT = 0
        STOPPED = 1
        RUNNING = 2
        STOPPING = 3
        STARTING = 4

    
    def __init__(self, server_list_file = None):
        self.state = self.State.NOT_INIT 
        
        if server_list_file is not None:
            self.resovle_server_list(server_list_file)

    def resovle_server_list(self, file_name):
        if self.state == self.State.RUNNING:
            print "can not resovle list file when monitor is running!"    
            return 
        self.server_list = list()

        with open(file_name) as f:
            for server_name in f.readlines():
                self.server_list.append(Server(server_name.replace("\n","")))
    def thread_func(self, server):
        #print str(server.check_state())
        state = server.check_state()
        if state.state == state.SERVER_STATE_UP:
            self.check_all_res_up.append(state)
        else:
            self.check_all_res_down.append(state)
        print "%d/%d\n" % tuple([len(self.check_all_res_up)+len(self.check_all_res_down), len(self.server_list)]),
    def check_all(self):
        threads = list()
        self.check_all_res_up = list()
        self.check_all_res_down = list()
        for s in self.server_list:
            threads.append(threading.Thread(target = self.thread_func, args=[s]))
        print "ping..." 
        for t in threads:
            t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()
        self.check_all_res_up = sorted(self.check_all_res_up, key = lambda state:state.time)    
        print "result:"
        for i in self.check_all_res_up:
            print i
        for i in self.check_all_res_down:
            #print i
            pass
        results = list()
        results.extend(self.check_all_res_up)
        results.extend(self.check_all_res_down)    
        return results 
if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "m":
        server_list_file = sys.argv[2]
        m = Monitor(server_list_file)
        print "%d servers in list." % len(m.server_list)
        m.check_all()
    elif len(sys.argv) == 2:
        s = Server(sys.argv[1])
        print s.check_state()
    else:
        server_list_file = "servers.list"
        m = Monitor(server_list_file)
        print "%d servers in list." % len(m.server_list)
        m.check_all()
    
