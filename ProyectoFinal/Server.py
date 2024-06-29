import tkinter as tk
import threading
import socket
import time as timesl
import pickle
import Pyro4
import sys
sys.path.append(".")


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

        #Thread to listen client requests
        #self.t1 = threading.Thread(target=self.reciveRequests)
        #self.t1.start()

        #Thread to adjust clock
        #self.t2 = threading.Thread(target=self.adjustHour)
        #self.t2.start()

        #Thread to refresh the interface
        #self.t4 = threading.Thread(target=self.refreshInterface)
        #self.t4.start()

    def reciveRequests(self):
        self.startNewSession()
        receiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiveSocket.bind((self.host_ip, 7900))

        while True:
            clientSock = receiveSocket.recvfrom(1024)
            if clientSock[0]:
                #Send hour to client
                hour = self.clock.returnHourTime()
                receiveSocket.sendto(pickle.dumps(hour), clientSock[1])
                #DB Queries
                userExists = self.bookDB.userExists(clientSock[1])
                if userExists != None:
                    self.syncUploadDB(userExists)
                self.requestBook(clientSock[1], hour) 
                #Send book to client
                receiveSocket.sendto(self.bookName.encode(), clientSock[1])

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
    
server = Server()