import socket
import pickle
import threading
import os
import sys

CHUNK_SIZE = 1024  # Tamaño del bloque

class Peer:
    def __init__(self, peer_id, tracker_host='127.0.0.1', tracker_port=5000):
        self.peer_id = peer_id
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.shared_files = {}
        self.downloaded_files = {}
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.tracker_host, self.tracker_port))
        self.register_with_tracker()
        threading.Thread(target=self.listen_for_requests, daemon=True).start()

    def register_with_tracker(self):
        request = {'action': 'register', 'peer_id': self.peer_id}
        self.client.send(pickle.dumps(request))

    def listen_for_requests(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 0))  # Vincula a cualquier puerto disponible
        server.listen(5)
        self.server_port = server.getsockname()[1]
        print(f"Peer escuchando en el puerto {self.server_port}")

        while True:
            client_socket, client_address = server.accept()
            threading.Thread(target=self.handle_peer_request, args=(client_socket,), daemon=True).start()

    def handle_peer_request(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if data:
                    request = pickle.loads(data)
                    action = request.get('action')

                    if action == 'request_chunk':
                        file_name = request.get('file_name')
                        chunk_index = request.get('chunk_index')
                        print(f"Peer {self.peer_id} - Enviando bloque {chunk_index} del archivo {file_name}")
                        self.send_chunk(client_socket, file_name, chunk_index)
                else:
                    break
        finally:
            client_socket.close()

    def send_chunk(self, client_socket, file_name, chunk_index):
        if file_name in self.shared_files:
            with open(self.shared_files[file_name], 'rb') as f:
                f.seek(chunk_index * CHUNK_SIZE)
                chunk_data = f.read(CHUNK_SIZE)
                response = {'chunk_index': chunk_index, 'chunk_data': chunk_data}
                client_socket.send(pickle.dumps(response))

    def list_files(self):
        request = {'action': 'list_files'}
        self.client.send(pickle.dumps(request))
        response = self.client.recv(4096)
        all_shared_files = pickle.loads(response)
        print("Archivos disponibles en el tracker:")
        for file in all_shared_files:
            print(f"Archivo: {file}")

    def share_file(self):
        file_path = input("Ingresa el path del archivo a compartir: ")
        file_name = os.path.basename(file_path)
        self.shared_files[file_name] = file_path
        request = {'action': 'share', 'peer_id': self.peer_id, 'file_name': file_name}
        self.client.send(pickle.dumps(request))
        print(f"Archivo {file_name} compartido exitosamente.")

    def download_file(self):
        file_name = input("Ingresa el nombre del archivo a descargar: ")
        self.downloaded_files[file_name] = []
        request = {'action': 'download', 'peer_id': self.peer_id, 'file_name': file_name}
        self.client.send(pickle.dumps(request))
        print(f"Iniciando descarga del archivo {file_name}...")

        peers_with_file = self.get_peers_with_file(file_name)
        if not peers_with_file:
            print(f"No se encontraron peers compartiendo el archivo {file_name}")
            return

        for peer in peers_with_file:
            self.download_chunks(file_name, peer)

    def get_peers_with_file(self, file_name):
        # Aquí deberías implementar la lógica para obtener la lista de peers que tienen el archivo
        # Para simplificar, aquí se devuelve una lista simulada
        return [('127.0.0.1', self.server_port)]  # Simula que el archivo está en el mismo peer

    def download_chunks(self, file_name, peer):
        peer_host, peer_port = peer
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((peer_host, peer_port))
        print(f"Conectado al peer {peer_host}:{peer_port} para descargar {file_name}")

        chunk_index = 0
        with open(file_name, 'wb') as f:
            while True:
                request = {'action': 'request_chunk', 'file_name': file_name, 'chunk_index': chunk_index}
                peer_socket.send(pickle.dumps(request))
                response = peer_socket.recv(4096)
                response_data = pickle.loads(response)

                if 'chunk_data' not in response_data or not response_data['chunk_data']:
                    break

                chunk_data = response_data['chunk_data']
                f.write(chunk_data)

                self.downloaded_files[file_name].append(chunk_index)
                print(f"Descargando bloque {chunk_index} del archivo {file_name}")
                self.update_progress(file_name, chunk_index, chunk_data)
                chunk_index += 1

        peer_socket.close()
        print(f"Descarga del archivo {file_name} completada.")

    def update_progress(self, file_name, chunk_index, chunk_data):
        total_size = os.path.getsize(file_name)
        current_size = chunk_index * CHUNK_SIZE + len(chunk_data)
        progress = (current_size / total_size) * 100
        sys.stdout.write(f"\rProgreso de descarga de {file_name}: {progress:.2f}%")
        sys.stdout.flush()

    def menu(self):
        while True:
            print("\n--- Menú del Peer ---")
            print("1. Listado de archivos disponibles")
            print("2. Opción de compartir archivo")
            print("3. Opción de descargar archivo")
            print("4. Cancelar acción")
            print("5. Salir del peer")
            choice = input("Elige una opción: ")

            if choice == '1':
                self.list_files()
            elif choice == '2':
                self.share_file()
            elif choice == '3':
                self.download_file()
            elif choice == '4':
                print("Acción cancelada.")
            elif choice == '5':
                self.client.close()
                break
            else:
                print("Opción inválida. Intenta de nuevo.")

if __name__ == "__main__":
    peer_id = input("Ingresa el ID del peer: ")
    peer = Peer(peer_id)
    peer.menu()
