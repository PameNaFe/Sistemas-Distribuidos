import socket
import threading

class Tracker:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.peers = []

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Tracker listening on {self.host}:{self.port}")

        while True:
            client, address = server.accept()
            print(f"Peer connected: {address}")
            self.peers.append(address)
            client.send(str(self.peers).encode())
            client.close()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
