import socket
import threading

class Tracker:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.files = {}  # {filename: [(peer_host, peer_port, is_complete, progress), ...]}
        self.peer_files = {}  # {(peer_host, peer_port): {filename: progress}}

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Tracker listening on {self.host}:{self.port}")

        while True:
            client, address = server.accept()
            print(f"Peer connected: {address}")
            message = client.recv(1024).decode()
            
            if message.startswith("SHARE"):
                parts = message.split()
                filename = parts[1]
                peer_host = parts[2]
                peer_port = int(parts[3])
                progress = int(parts[4])  # progreso de la compartición
                
                if filename in self.files:
                    self.files[filename].append((peer_host, peer_port, True, progress))
                else:
                    self.files[filename] = [(peer_host, peer_port, True, progress)]

                if (peer_host, peer_port) not in self.peer_files:
                    self.peer_files[(peer_host, peer_port)] = {}
                self.peer_files[(peer_host, peer_port)][filename] = progress
                
                # Informar a los peers sobre la actualización
                client.send(str(self.files[filename]).encode())

            elif message.startswith("DOWNLOAD"):
                parts = message.split()
                filename = parts[1]
                peer_host = parts[2]
                peer_port = int(parts[3])
                progress = int(parts[4])  # progreso de la descarga

                if filename in self.files:
                    self.files[filename].append((peer_host, peer_port, False, progress))
                else:
                    self.files[filename] = [(peer_host, peer_port, False, progress)]

                if (peer_host, peer_port) not in self.peer_files:
                    self.peer_files[(peer_host, peer_port)] = {}
                self.peer_files[(peer_host, peer_port)][filename] = progress

                client.send(str(self.files[filename]).encode())

            elif message.startswith("LIST"):
                client.send(str(self.files).encode())

            client.close()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
