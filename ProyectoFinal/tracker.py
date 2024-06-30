import socket
import threading
import json

class Tracker:
    def __init__(self, host='192.168.1.74', port=5000):
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
        
        try:
            request = json.loads(message)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON message from {address} - {e}")
            client.close()
            return
        
        action = request.get("action")

        if action == "share":
            filename = request.get("filename")
            peer_host = request.get("host")
            peer_port = request.get("port")
            progress = request.get("progress")

            if filename in self.files:
                self.files[filename].append((peer_host, peer_port, True, progress))
            else:
                self.files[filename] = [(peer_host, peer_port, True, progress)]

            if (peer_host, peer_port) not in self.peer_files:
                self.peer_files[(peer_host, peer_port)] = {}
            self.peer_files[(peer_host, peer_port)][filename] = progress
            
            client.send(json.dumps(self.files[filename]).encode())

        elif action == "download":
            filename = request.get("filename")
            peer_host = request.get("host")
            peer_port = request.get("port")
            progress = request.get("progress")

            if filename in self.files:
                self.files[filename].append((peer_host, peer_port, False, progress))
            else:
                self.files[filename] = [(peer_host, peer_port, False, progress)]

            if (peer_host, peer_port) not in self.peer_files:
                self.peer_files[(peer_host, peer_port)] = {}
            self.peer_files[(peer_host, peer_port)][filename] = progress

            client.send(json.dumps(self.files[filename]).encode())

        elif action == "list":
            client.send(json.dumps(self.files).encode())
        else:
            client.send(json.dumps({}).encode())  # Responder con un JSON vacío si la acción no es válida

        client.close()

if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
