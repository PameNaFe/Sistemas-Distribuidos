import Pyro4


class Client():
    tracker = Pyro4.Proxy("PYRO:tracker@localhost:55300")

#Si NO tiene archivo 
    #Cliente
#Si solo tiene una parte del archivo
    #Leecher

#    def client(self):
        
        
#    def clientLeecher(self):