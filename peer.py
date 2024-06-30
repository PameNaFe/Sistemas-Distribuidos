import socket
import threading
import time
import os

class Peer:
    def __init__(self, id, host='127.0.0.1', port=5001, tracker_host='127.0.0.1', tracker_port=5000):
        self.id = id
        self.host = host
        self.port = port + id
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.files = {}  # {filename: [is_complete, progress]}
        self.peers = []
        self.is_seeder = False

    def connect_to_tracker(self):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        tracker.send(b"LIST")
        files = tracker.recv(1024).decode()
        self.peers = eval(files)
        tracker.close()
        print(f"Peer {self.id} connected to tracker, peers: {self.peers}")

    def register_file_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        
        # Informar al tracker sobre el archivo compartido
        message = f"SHARE {filename} {self.host} {self.port} {progress}"
        tracker.send(message.encode())
        
        # Actualizar lista de peers desde el tracker
        peers = tracker.recv(1024).decode()
        self.peers = eval(peers)
        tracker.close()

    def register_download_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        
        # Informar al tracker sobre el progreso de la descarga
        message = f"DOWNLOAD {filename} {self.host} {self.port} {progress}"
        tracker.send(message.encode())
        
        # Actualizar lista de peers desde el tracker
        peers = tracker.recv(1024).decode()
        self.peers = eval(peers)
        tracker.close()

    def start(self):
        threading.Thread(target=self.server).start()
        self.connect_to_tracker()
        self.client()

    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Peer {self.id} listening on {self.host}:{self.port}")

        while True:
            client, address = server.accept()
            filename = client.recv(1024).decode()
            if filename in self.files and self.files[filename][0]:
                client.send(b'ACK')
                with open(filename, 'rb') as f:
                    client.sendfile(f)
            client.close()

    def client(self):
        while True:
            command = input(f"Peer {self.id}, ingresa la acción ('share [filename]' para compartir, 'download [filename]' para obtener, 'list' para ver archivos en el tracker, 'cancel [filename]' para cancelar): ")
            if command.startswith('share '):
                filename = command.split(' ')[1]
                if os.path.exists(filename):
                    self.files[filename] = [True, 100]
                    self.is_seeder = True
                    print(f"Peer {self.id} is now sharing {filename}")
                    
                    # Registrar archivo con el tracker
                    self.register_file_with_tracker(filename, 100)
                    
                else:
                    print(f"File {filename} does not exist.")
            elif command.startswith('download '):
                filename = command.split(' ')[1]
                self.files[filename] = [False, 0]
                threading.Thread(target=self.download_file, args=(filename,)).start()
            elif command == 'list':
                self.connect_to_tracker()
                print("Archivos en el tracker:", self.peers)
            elif command.startswith('cancel '):
                filename = command.split(' ')[1]
                if filename in self.files:
                    del self.files[filename]
                    print(f"Cancelled sharing/downloading of {filename}")
            else:
                print("Invalid command.")

    def download_file(self, filename):
        for peer_host, peer_port, is_complete, progress in self.peers.get(filename, []):
            if peer_host == self.host and peer_port == self.port:
                continue
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((peer_host, peer_port))
                client.send(filename.encode())
                response = client.recv(1024)
                if response == b'ACK':
                    with open(f"{filename}_part_{self.id}", 'wb') as f:
                        while True:
                            data = client.recv(1024)
                            if not data:
                                break
                            f.write(data)
                            self.files[filename][1] += len(data)
                            percentage = (self.files[filename][1] / os.path.getsize(filename)) * 100
                            print(f"Downloading {filename}: {percentage:.2f}%")
                            self.register_download_with_tracker(filename, int(percentage))
                    self.files[filename] = [True, 100]
                    print(f"Peer {self.id} completed download of {filename}")
                    client.close()
                    break
            except Exception as e:
                print(f"Failed to download from {peer_host}:{peer_port}, error: {e}")
                continue

if __name__ == "__main__":
    peer_id = int(input("Enter peer ID: "))
    peer = Peer(peer_id)
    peer.start()
