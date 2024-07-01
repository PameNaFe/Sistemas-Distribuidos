import socket
import pickle
import threading

class Tracker:
    def __init__(self, host='127.0.0.1', port=5000):
        self.peers = {}
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print(f"Tracker escuchando en {self.host}:{self.port}")
        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            client_socket, client_address = self.server.accept()
            print(f"Conexión aceptada de {client_address}")
            threading.Thread(target=self.handle_peer, args=(client_socket,)).start()

    def handle_peer(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if data:
                    request = pickle.loads(data)
                    if request['action'] == 'register':
                        self.peers[request['peer_id']] = {'shared_files': [], 'downloaded_files': [], 'progress': 0}
                        print(f"Peer registrado: {request['peer_id']}")
                    elif request['action'] == 'share':
                        self.peers[request['peer_id']]['shared_files'].append(request['file_name'])
                        print(f"Archivo compartido por {request['peer_id']}: {request['file_name']}")
                    elif request['action'] == 'progress_update':
                        self.peers[request['peer_id']]['progress'] = request['progress']
                    elif request['action'] == 'download':
                        self.peers[request['peer_id']]['downloaded_files'].append(request['file_name'])
                        threading.Thread(target=self.simulate_download, args=(request['peer_id'],)).start()
                        print(f"Descargando archivo para {request['peer_id']}: {request['file_name']}")
                    elif request['action'] == 'list_files':
                        all_shared_files = self.get_all_shared_files()
                        client_socket.send(pickle.dumps(all_shared_files))
                    self.save_data()
                else:
                    break
        finally:
            client_socket.close()

    def simulate_download(self, peer_id):
        for progress in range(0, 101, 10):
            self.peers[peer_id]['progress'] = progress
            self.save_data()
            threading.Event().wait(1)  # Simulación de tiempo de descarga

    def get_all_shared_files(self):
        all_files = []
        for peer_id, info in self.peers.items():
            all_files.extend(info['shared_files'])
        return all_files

    def save_data(self):
        with open('tracker_data.pkl', 'wb') as f:
            pickle.dump(self.peers, f)

    def menu(self):
        while True:
            print("\n--- Menú del Tracker ---")
            print("1. Visualizar todos los peers conectados")
            print("2. Ver la cantidad de archivos descargados y compartidos")
            print("3. Visualizar el progreso de las descargas o subidas de archivos por cada peer")
            print("4. Obtener listado de los archivos compartidos por los peers")
            print("5. Salir del tracker")
            choice = input("Elige una opción: ")

            if choice == '1':
                self.display_peers()
            elif choice == '2':
                self.display_files_stats()
            elif choice == '3':
                self.display_progress()
            elif choice == '4':
                self.list_shared_files()
            elif choice == '5':
                self.server.close()
                break
            else:
                print("Opción inválida. Intenta de nuevo.")

    def display_peers(self):
        print("Peers conectados:")
        for peer_id, info in self.peers.items():
            print(f"ID: {peer_id}, Archivos Compartidos: {len(info['shared_files'])}, Archivos Descargados: {len(info['downloaded_files'])}")

    def display_files_stats(self):
        print("Archivos compartidos y descargados:")
        for peer_id, info in self.peers.items():
            print(f"ID: {peer_id}, Compartidos: {len(info['shared_files'])}, Descargados: {len(info['downloaded_files'])}")

    def display_progress(self):
        print("Progreso de las descargas/subidas:")
        for peer_id, info in self.peers.items():
            print(f"ID: {peer_id}, Progreso: {info['progress']}%")

    def list_shared_files(self):
        print("Archivos compartidos por los peers:")
        for peer_id, info in self.peers.items():
            print(f"ID: {peer_id}, Archivos: {info['shared_files']}")

if __name__ == "__main__":
    tracker = Tracker()
    tracker.menu()
