import tkinter as tk
import threading
import socket
import time as timesl
import Pyro4
import sys
sys.path.append(".")

#Si se tiene TODO el archivo
    #Servidor - Seeder
#Si NO tiene TODO el archivo
    #Servidor - Leecher
#Si NO tiene el archivo
    #Cliente

class Server(tk.Frame):
    tracker = Pyro4.Proxy("PYRO:tracker@localhost:55300")
    
    def _init_(self):
        self.new_host = True
        self.host_name = 'Host1'
        self.host_ip = '192.168.0.2'
        self.avaliable_resources = ['A', 'B']

        #Thread for synchronizing DB
        self.t3 = threading.Thread(target=self.notifyTracker)
        self.t3.start()
        timesl.sleep(1)

    #mi_socket = socket.socket()


    #ejecuta hilo
    def notifyTracker(self):
        resource_count = 0
        if self.new_host:
            self.tracker.identifyHost(self.host_name, self.host_ip, self.avaliable_resources)
            resource_count = self.resource_count
        else:
            while(True):
                if resource_count != self.resource_count:
                    self.tracker.putResource(self.host_name, self.avaliable_resources[resource_count-1])
                    resource_count += 1
                    timesl.sleep(0.5)
    print(notifyTracker)
    #Seeder
   # def serverSeeder(self):
    #    if self.tracker.is_alive():

    #Leecher
    #def serverLeecher(self):
    
server = Server()