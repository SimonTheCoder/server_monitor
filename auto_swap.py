#!/usr/bin/python

import sys
import subprocess
import threading
import monitor
import json
import time

class Looper:

    def __init__(self,exec_path, config_path, duration, host_list):

        self.exec_path  = exec_path 
        self.config_path = config_path
        self.duration = duration
        self.host_list = host_list

        self.started = False
        self.thread = threading.Thread(target=self.loop)
        self.thread.setDaemon(True)
        self.monitor = monitor.Monitor(host_list)
        self.last_fast = None
        self.popen = None

    def loop(self):
        while self.started is True:
            #find fastest server
            states = self.monitor.check_all()
            
            if states[0].state > 0:
                fast_ip = states[0].ip
                if self.last_fast == fast_ip:
                    print "still the same one."
                    #print self.popen.stdout.readline()
                else:
                    #load config file
                    config_dict = None
                    with open(self.config_path, "r") as config_fd:
                        config_dict = json.load(config_fd)
                    
                    print "server: %s -> %s " % (config_dict["server"], fast_ip)
                    self.last_fast = fast_ip
                    config_dict["server"] = fast_ip

                    with open(self.config_path, "w") as config_fd:
                        json.dump(config_dict, config_fd)
                    
                    
                    if self.popen is not None:
                        print "restarting..."
                        self.popen.terminate()
                    else:
                        print "starting..."
                    self.popen = subprocess.Popen([self.exec_path,"-c",self.config_path],stderr=subprocess.PIPE)
                err_times = 0
                for stdout_line in iter(self.popen.stderr.readline, ""):
                    print "ss:" + stdout_line,
                    if stdout_line.find("ERROR") != -1:
                        err_times = err_times + 1
                        print "%d Errors found. check servers!" % (err_times)
                       
                        if err_times > 10:
                            print "error times > 10, recheck..."
                            err_times = 0
                            break

                        single_server = monitor.Server(fast_ip)
                        single_server_state = single_server.check_state()
                        if single_server_state.state >0:
                            print "server still working."
                            continue
                        else:    
                            print "server down."
                            print single_server_state
                            break
            else:
                print "no available host found!!!!"

            time.sleep(self.duration)
            

    
    def start_looper(self, using_thread = False):
        self.started = True

        if using_thread is True:
            print "still in working..."
        else:
            self.loop()
        pass
    

    def stop_looper(self):
        self.started = False
        pass



if __name__ == "__main__":
    if len(sys.argv) == 5:
        exec_path = sys.argv[1]
        config_path = sys.argv[2]
        duration = int(sys.argv[3],10)
        host_list = sys.argv[4]

        print "exec: %s\nconf: %s\nduration: %s\nhost_list: %s\n" % (exec_path, config_path, duration, host_list)


        looper = Looper(exec_path, config_path, duration, host_list)
        looper.start_looper()

                
