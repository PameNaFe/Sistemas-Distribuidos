# peer
import socket
import threading
import os
import sys
import json  # Usar JSON para la serialización de datos

class Peer:
    def __init__(self, id, host='192.168.1.74', port=5001, tracker_host='192.168.1.74', tracker_port=5000):
        self.id = id
        self.host = host
        self.port = port + id
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.files = {}  # {filename: [is_complete, progress]}
        self.peers = {}
        self.is_seeder = False

    def connect_to_tracker(self):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        tracker.send(json.dumps({"action": "list"}).encode())
        files = tracker.recv(12_500_000).decode()

        if files:  # Verificar si se recibió alguna respuesta
            try:
                self.peers = json.loads(files)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from tracker: {e}")
                self.peers = {}
        else:
            print("No response from tracker")
            self.peers = {}

        tracker.close()

    def register_file_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        message = {
            "action": "share",
            "filename": filename,
            "host": self.host,
            "port": self.port,
            "progress": progress
        }
        tracker.send(json.dumps(message).encode())
        # 100 Megabits son 12.5 Megabytes
        # Recibir hasta 12,500,000 bytes (12.5 MB) desde el tracker
        peers = tracker.recv(12_500_000).decode()

        if peers:
            try:
                self.peers = json.loads(peers)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from tracker: {e}")
                self.peers = {}
        else:
            print("No response from tracker")
            self.peers = {}

        tracker.close()

    def register_download_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        message = {
            "action": "download",
            "filename": filename,
            "host": self.host,
            "port": self.port,
            "progress": progress
        }
        tracker.send(json.dumps(message).encode())
        peers = tracker.recv(1024).decode()

        if peers:
            try:
                self.peers = json.loads(peers)
            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON desde el tracker: {e}")
                self.peers = {}
        else:
            print("Sin respuesta del tracker")
            self.peers = {}

        tracker.close()

    def update_progress_with_tracker(self, filename, progress):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker.connect((self.tracker_host, self.tracker_port))
        message = {
            "action": "progress",
            "filename": filename,
            "host": self.host,
            "port": self.port,
            "progress": progress
        }
        tracker.send(json.dumps(message).encode())
        tracker.close()

    def start(self):
        threading.Thread(target=self.server).start()
        self.connect_to_tracker()
        self.client()

    def server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Peer {self.id} escuchando en {self.host}:{self.port}")

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
            print(f"\nBienvenido, Peer {self.id}")
            print("1. Listado del tracker")
            print("2. Compartir archivo ('share [nombre_archivo]')")
            print("3. Descargar archivo ('download [nombre_archivo]')")
            print("4. Cancelar acción ('cancel [nombre_archivo]')")
            print("5. Salir")
            command = input("\nSelecciona una opción: ")

            if command == '1':
                self.list_files()
            elif command.startswith('share '):
                filename = command.split(' ')[1]
                self.share_file(filename)
            elif command.startswith('download '):
                filename = command.split(' ')[1]
                self.files[filename] = [False, 0]
                threading.Thread(target=self.download_file, args=(filename,)).start()
            elif command.startswith('cancel '):
                filename = command.split(' ')[1]
                self.cancel_action(filename)
            elif command == '5':
                print(f"Peer {self.id} desconectado. ¡Hasta luego!")
                sys.exit()  # Sale del programa
            else:
                print("\nComando inválido.")

    def list_files(self):
        self.connect_to_tracker()
        files_list = "\n".join(self.peers)  # Agrega un salto de línea entre cada archivo
        print("\nArchivos en el tracker:\n", files_list)

    def share_file(self, filename):
        if os.path.exists(filename):
            self.files[filename] = [True, 100]
            self.is_seeder = True
            print(f"Peer {self.id} está compartiendo {filename}")

            # Registrar archivo con el tracker
            self.register_file_with_tracker(filename, 100)
            print(f"\nArchivo compartido con éxito.")
        else:
            print(f"\nEl archivo {filename} no existe.")

    def download_file(self, filename):
        if filename not in self.peers:
            print(f"El archivo {filename} no está disponible en el tracker")
            return

        for peer_info in self.peers[filename]:
            peer_host, peer_port, is_complete, progress = peer_info
            if peer_host == self.host and peer_port == self.port:
                continue
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((peer_host, peer_port))
                client.send(filename.encode())
                response = client.recv(1024)
                if response == b'ACK':
                    with open(filename, 'wb') as f:  # Ajustado para mantener el nombre original
                        total_downloaded = 0
                        while True:
                            data = client.recv(1024)
                            if not data:
                                break
                            f.write(data)
                            total_downloaded += len(data)
                            self.files[filename][1] = total_downloaded
                            # Asegurarse de que el tamaño del archivo no sea cero
                            try:
                                file_size = os.path.getsize(filename)
                                if file_size > 0:
                                    percentage = (total_downloaded / file_size) * 100
                                    self.update_progress_with_tracker(filename, int(percentage))
                                    print(f"Descargando {filename}: {percentage:.2f}%")
                                else:
                                    print("El tamaño del archivo es cero, no se puede calcular el progreso")
                            except OSError as e:
                                print(f"Error al obtener el tamaño del archivo: {e}")
                    self.files[filename] = [True, 100]
                    print(f"\nPeer {self.id} completó la descarga de {filename}")
                    client.close()
                    break
            except Exception as e:
                print(f"Falló la descarga desde {peer_host}:{peer_port}, error: {e}")
                continue



    def cancel_action(self, filename):
        if filename in self.files:
            del self.files[filename]
            print(f"Cancelada la acción de compartir/descargar de {filename}")
        else:
            print(f"El archivo {filename} no se está compartiendo ni descargando.")

if __name__ == "__main__":
    peer_id = int(input("Ingresa el ID del peer: "))
    peer = Peer(peer_id)
    peer.start()
