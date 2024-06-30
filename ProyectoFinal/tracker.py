import socket
import threading

class Tracker:
    def __init__(self, host='192.168.0.19', port=5000): # La dirección IP debe ser la qut tenga la PC/Laptop

        self.host = host
        self.port = port
        self.files = {}  # {filename: [(peer_host, peer_port, is_complete, progress), ...]}
        self.peer_files = {}  # {(peer_host, peer_port): {filename: progress}}

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((self.host, self.port))
        except socket.error as e:
            print(f"Error binding to {self.host}:{self.port} - {e}")
            return

        server.listen(5)
        print(f"Tracker listening on {self.host}:{self.port}")

        while True:
            try:
                client, address = server.accept()
                threading.Thread(target=self.handle_client, args=(client, address)).start()
            except Exception as e:
                print(f"Error accepting connection - {e}")

    def handle_client(self, client, address):
        peer_id = address[1] - 5001  # Calcula el ID del peer según su puerto
        print(f"Peer {peer_id} connected: {address}")
        try:
            message = client.recv(1024).decode()
        except Exception as e:
            print(f"Error receiving message from {address} - {e}")
            client.close()
            return
        
        if message.startswith("share"):
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

        elif message.startswith("download"):
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

        elif message.startswith("list"):
            client.send(str(self.files).encode())

        client.close()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
