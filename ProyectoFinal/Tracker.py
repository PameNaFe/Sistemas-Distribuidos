import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Tracker(object):
    def __init__(self):
        self.listPeers = []
        self.listFiles = []

    def getFile(self):
        newFiles = []
    
    def setFile(self):
        newFile = []


        


def main():
    Pyro4.Daemon.serveSimple(
        {Tracker: "torrentS"},
        host="10.0.0.13",
        port=17000,
        ns=False
    )