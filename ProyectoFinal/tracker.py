# tracker
import socket
import threading
import json

class Tracker:
    def __init__(self, host='192.168.1.74', port=5000):
        self.host = host
        self.port = port
        self.files = {}  # {filename: [(peer_host, peer_port, is_complete, progress), ...]}
        self.peer_files = {}  # {(peer_host, peer_port): {filename: progress}}
        self.connected_peers = []  # List to keep track of connected peers

    def start(self):
        threading.Thread(target=self.server).start()
        self.console_menu()

    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((self.host, self.port))
        except socket.error as e:
            print(f"Error binding to {self.host}:{self.port} - {e}")
            return

        server.listen(5)
        print(f"Tracker escuchando en {self.host}:{self.port}")

        while True:
            try:
                client, address = server.accept()
                self.connected_peers.append((client, address))
                threading.Thread(target=self.handle_client, args=(client, address)).start()
            except Exception as e:
                print(f"Error accepting connection - {e}")

    def handle_client(self, client, address):
        peer_id = address[1] - 5001  # Calcula el ID del peer según su puerto
        try:
            message = client.recv(12_500_000).decode()
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
        filename = request.get("filename")
        peer_host = request.get("host")
        peer_port = request.get("port")
        progress = request.get("progress", 0)

        if action == "share":
            if filename in self.files:
                self.files[filename].append((peer_host, peer_port, True, progress))
            else:
                self.files[filename] = [(peer_host, peer_port, True, progress)]

            if (peer_host, peer_port) not in self.peer_files:
                self.peer_files[(peer_host, peer_port)] = {}
            self.peer_files[(peer_host, peer_port)][filename] = progress

            client.send(json.dumps(self.files[filename]).encode())

        elif action == "download":
            if filename in self.files:
                for i, (host, port, is_complete, prog) in enumerate(self.files[filename]):
                    if host == peer_host and port == peer_port:
                        self.files[filename][i] = (peer_host, peer_port, False, progress)
                        break
                else:
                    self.files[filename].append((peer_host, peer_port, False, progress))
            else:
                self.files[filename] = [(peer_host, peer_port, False, progress)]

            if (peer_host, peer_port) not in self.peer_files:
                self.peer_files[(peer_host, peer_port)] = {}
            self.peer_files[(peer_host, peer_port)][filename] = progress

            client.send(json.dumps(self.files[filename]).encode())

        elif action == "progress":
            if filename in self.files:
                for i, (host, port, is_complete, prog) in enumerate(self.files[filename]):
                    if host == peer_host and port == peer_port:
                        self.files[filename][i] = (peer_host, peer_port, is_complete, progress)
                        break
            if (peer_host, peer_port) in self.peer_files:
                self.peer_files[(peer_host, peer_port)][filename] = progress

            # Mostrar el progreso
            print(f"Progreso de {filename} desde {peer_host}:{peer_port}: {progress}%")

        elif action == "list":
            client.send(json.dumps(self.files).encode())
        else:
            client.send(json.dumps({}).encode())  # Responder con un JSON vacío si la acción no es válida

        client.close()

    def show_peer_status(self):
        print("Estado de cada Peer conectado:")
        for client, address in self.connected_peers:
            peer_id = address[1] - 5001
            print(f"Peer {peer_id} connected: {address}")
       

    def debug_info(self):
        print("Información de archivos:")
        print("Archivos compartidos:")
        for filename, peers in self.files.items():
            print(f"  {filename}:")
            for peer_info in peers:
                print(f"    Peer {peer_info[0]}:{peer_info[1]} - Completo: {peer_info[2]}, Progreso: {peer_info[3]}%")

        print("Archivos por Peer:")
        for peer, files in self.peer_files.items():
            print(f"  Peer {peer[0]}:{peer[1]}:")
            for filename, progress in files.items():
                print(f"    {filename} - Progreso: {progress}%")

    def download_progress(self):
         for peer, files in self.peer_files.items():
            print(f"  Peer {peer[0]}:{peer[1]}:")
            for filename, progress in files.items():
                is_complete = any(f[2] for f in self.files.get(filename, []) if f[0] == peer[0] and f[1] == peer[1])
                status = "Completo" if is_complete else f"Progreso: {progress}%"
                print(f"    {filename} - {status}")

    def console_menu(self):
        while True:
            print("\nMenú del Tracker:")
            print("1. Ver estado de cada peer conectado")
            print("2. Archivos")
            print("3. Progreso de descargas")
            print("4. Salir")
            option = input("Seleccione una opción: ")

            if option == '1':
                self.show_peer_status()
            elif option == '2':
                self.debug_info()
            elif option == '3':
                self.download_progress()
            elif option == '4':
                print("Tracker desconectado. ¡Hasta luego!")
                break
            else:
                print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    tracker = Tracker()
    tracker.start()
